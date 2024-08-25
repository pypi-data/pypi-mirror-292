from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Any, Callable, ClassVar, Generator, List, Optional, Tuple

import numpy as np
from beet import Context, DataPack
from beet import Generator as BeetGenerator
from beet import JsonFile, NamespaceFileScope
from beet.core.utils import required_field
from bolt import Runtime
from bolt_control_flow import BranchInfo, Case, CaseResult, WrappedCases
from colorama import init
from mecha import (
    AstChildren,
    AstCommand,
    AstCommandSentinel,
    AstJson,
    AstNode,
    AstRoot,
    Diagnostic,
    Mecha,
    MutatingReducer,
    Serializer,
    Visitor,
    rule,
)
from tokenstream import set_location

RED = "\033[91m"
YELLOW = "\033[38;5;214m"
BLUE = "\033[36m"
DARK_GREY = "\033[90m"
RESET = "\033[0m"


class ErrorType(Enum):
    ERROR = RED
    WARNING = YELLOW


def getError(error_type: ErrorType, file_path, error_text):
    result = None
    with open(file_path, "r") as file:
        lines = file.readlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("elif") and ".get_phase() ==" in line:
            # Get the relevant line information
            current_line = line.strip()
            column_number = line.find("elif") + 1
            line_number = i  # Line number is 1-based

            # Get the content of the line before
            if i > 0:
                prev_line = lines[i - 1].strip()
            else:
                prev_line = None

            # Get the content of the line after
            if i < len(lines) - 1:
                next_line = lines[i + 1].strip()
            else:
                next_line = None

            # Collect the results in a dictionary
            result = {
                'line_number': line_number,
                'column_number': column_number,
                'prev_line': prev_line,
                'current_line': current_line,
                'next_line': next_line
            }
    if result is not None:
        line_number = result["line_number"]
        column_number = result["column_number"]
        line_texts = [value for key, value in result.items() if key != "line_number" and key != "column_number"]
        current_file = Path(__file__).stem
        color = error_type.value
        return f"""{color}{error_type.name}  |{RESET} {DARK_GREY}{current_file}{RESET}  {color}{error_text}{RESET}
{' ' * len(error_type.name)}  {color}|{RESET} {BLUE}{file_path}:{line_number}:{column_number}{RESET}
{' ' * len(error_type.name)}  {color}|{RESET}     {line_number - 1} |      {line_texts[0]}
{' ' * len(error_type.name)}  {color}|{RESET}     {line_number} |      {line_texts[1]} 
{' ' * len(error_type.name)}  {color}|{RESET}     {" " * len(str(line_number))} :    {' ' * (column_number - 1)} ^{'^' * (len(line_texts[1]) - 1)}
{' ' * len(error_type.name)}  {color}|{RESET}     {line_number + 1} |      {line_texts[2]}"""


class EquipmentSlot(Enum):
    MAINHAND = "mainhand"
    OFFHAND = "offhand"
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"

# the plugin entrypoint that gets called when
# the plugin is required in a pipeline
def apoli(ctx: Context):
    init()
    """The Apoli plugin."""
    ctx.require("bolt_control_flow")

    # register power data pack resource
    ctx.data.extend_namespace.append(PowerFile)
    runtime = ctx.inject(Runtime)
    runtime.globals["entity"] = Entity(ctx)
    runtime.globals["block"] = Block(ctx)
    runtime.globals["power"] = Power(ctx)
    runtime.globals["Raycast"] = Raycast(ctx)
    runtime.globals["MetaUtils"] = MetaUtils(ctx)

    mecha = ctx.inject(Mecha)
    # extend mecha transform with the Apoli transformer
    converter = ApoliJsonConverter(serialize=mecha.serialize)
    mecha.transform.extend(
        ApoliTransformer(generate=ctx.generate, pack=ctx.data, converter=converter)
    )


beet_default = apoli


class PowerFile(JsonFile):
    """Class representing a power file."""

    scope: ClassVar[NamespaceFileScope] = ("powers",)
    extension: ClassVar[str] = ".json"


# region AST Nodes
# the command ast nodes that keep apoli-specific ast.
# sentinel commands are useful for storing data that is processed
# in later compilation steps and does not emit any command directly in
# the output pack
@dataclass(frozen=True, kw_only=True)
class AstApoliCommand(AstCommandSentinel):
    arguments: AstChildren["AstApoliTypedObject"] = AstChildren()


@dataclass(frozen=True, kw_only=True)
class AstApoliPowerCommand(AstApoliCommand):
    resource_location: str
    arguments: AstChildren["AstApoliPower"] = AstChildren()


@dataclass(frozen=True, kw_only=True)
class AstApoliField(AstNode):
    key: str
    value: AstNode


@dataclass(frozen=True, kw_only=True)
class AstApoliTypedObject(AstNode):
    type: str
    fields: AstChildren[AstApoliField] = AstChildren()


@dataclass(frozen=True, kw_only=True)
class AstApoliPower(AstApoliTypedObject):
    file_name: str
    file_subname: str
    type: str
    name: str
    description: str
    condition: "AstApoliCondition"


@dataclass(frozen=True, kw_only=True)
class AstApoliMultiplePower(AstApoliPower):
    pass


@dataclass(frozen=True, kw_only=True)
class AstApoliCondition(AstApoliTypedObject):
    type: str
    inverted: bool = False


@dataclass(frozen=True, kw_only=True)
class AstApoliAction(AstApoliTypedObject):
    type: str


@dataclass(frozen=True, kw_only=True)
class AstApoliLiteral(AstNode):
    value: Any | List[Any]


# endregion

def create_command_action(type: str, **fields: Any) -> AstApoliAction:
    ast_fields = AstChildren(
        AstApoliCommand(
            identifier=key,
            arguments=AstApoliLiteral(value=value)
            if not isinstance(value, AstNode)
            else value,
        )
        for key, value in fields.items()
    )
    return AstApoliAction(type=type, fields=ast_fields)


def create_action(type: str, **fields: Any) -> AstApoliAction:
    ast_fields = AstChildren(
        AstApoliField(
            key=key,
            value=AstApoliLiteral(value=value)
            if not isinstance(value, AstNode)
            else value,
        )
        for key, value in fields.items()
    )
    return AstApoliAction(type=type, fields=ast_fields)


def create_condition(ctx: Context, type: str, inverted: bool = False, **fields: Any) -> "Condition":
    ast_fields = AstChildren(
        AstApoliField(
            key=key,
            value=AstApoliLiteral(value=value)
            if not isinstance(value, AstNode)
            else value,
        )
        for key, value in fields.items()
    )
    return Condition(ctx=ctx, type=type, inverted=inverted, fields=ast_fields)


def unwrap_action(commands: AstChildren[AstCommand]) -> AstNode | AstApoliAction | None:
    """Takes a list of commands and returns the equivalent apoli action"""
    # return the single nested apoli action
    if len(commands) == 1 and isinstance(command := commands[0], AstApoliCommand):
        return command.arguments[0]
    # turns a list of commands that contain both normal commands and
    # apoli sentinel commands into an apoli:and action.
    #
    # adjacent commands are clumped together into a single apoli:execute_command action,
    # while each apoli command sentinel becomes a separate action.
    if any(isinstance(command, AstApoliCommand) for command in commands):
        parts: list[list[AstCommand]] = [[]]

        # splits the commands so that apoli sentinel commands are separated
        # from normal commands
        for command in commands:
            if isinstance(command, AstApoliCommand):
                parts.append([command])
                parts.append([])
            else:
                parts[-1].append(command)

        if len(parts) > 1:
            parts = [cmds for cmds in parts if len(cmds)]

        # wrap each child action individually
        return create_action(type="apoli:and", actions=AstChildren(unwrap_action(AstChildren(cmds)) for cmds in parts))

    # create a apoli:execute_command if there are only normal commands
    #
    # this is a trick for wrapping the ast root in a "execute run: ..." command
    # and letting the mecha.contrib.nesting plugin either inline single-commands or
    # create an anonymous function
    if len(commands) == 0:
        return None
    return create_action(type="apoli:execute_command",
                         command=AstCommand(
                             identifier="execute:subcommand",
                             arguments=AstChildren(
                                 (
                                     AstCommand(
                                         identifier="execute:commands",
                                         arguments=AstChildren((AstRoot(commands=commands),)),
                                     ),
                                 )
                             ),
                         )
                         )


# The main class for interacting with apoli conditions.
#
# Implements `__not__`, `__branch__` and `__multibranch__`
# which overloads the default behaviour of bolt syntax.
# Additionally, `__logical_and__` and `__logical_or__` could also be overloaded.
#
# `__branch__` and `__multibranch__`, when called, emit the sentinel commands to
# temporarily store the generated apoli ast.
@dataclass
class Condition:
    ctx: Context = field(repr=False)
    type: str
    fields: AstChildren[AstApoliField]
    inverted: bool = False

    @property
    def runtime(self):
        return self.ctx.inject(Runtime)

    def to_ast(self) -> AstApoliCondition:
        return AstApoliCondition(type=self.type, inverted=self.inverted, fields=self.fields)

    def __logical_and__(self, other):
        return create_condition(self.ctx, type="apoli:and", conditions=[self.to_ast(), other().to_ast()])

    def __logical_or__(self, other):
        return create_condition(self.ctx, type="apoli:or", conditions=[self.to_ast(), other().to_ast()])

    def __not__(self):
        return replace(self, inverted=not self.inverted)

    @contextmanager
    def __branch__(self):
        with self.runtime.scope() as cmds:
            yield True

        if_action = unwrap_action(AstChildren(cmds))
        if len(self.fields) > 0 and self.fields[0].key == "internal:phase_value":
            if isinstance(self.fields[0].value, AstApoliLiteral):
                test = AstApoliField(key=self.fields[0].value.value, value=if_action)
                action = create_action(type=self.fields[0].key, value=test)
                command = AstApoliCommand(arguments=AstChildren((action,)))
                self.runtime.commands.append(command)
                return
        action = create_action(type="apoli:if_else", condition=self.to_ast(), if_action=if_action)
        command = AstApoliCommand(arguments=AstChildren((action,)))
        self.runtime.commands.append(command)

    @contextmanager
    def __multibranch__(self, info: BranchInfo):
        case = ActionIfElseCase(self.ctx)
        yield case

        if self.fields[0].key == "internal:phase_value":
            print(getError(ErrorType.WARNING, self.get_path(),
                           "Cannot have \"if-elif-else\" when checking phases of powers."))
            return

        if_action = unwrap_action(case.if_commands)
        else_action = unwrap_action(case.else_commands)

        # this produces nested apoli:if_else actions. you could check if `else_action`
        # is AstApolifIfElse or AstApoliIfElifElse node and flatten all cases into
        # a single AstApoliIfElifElse node. this could also be done in ApoliTransformer
        # as a separate rule.
        action = create_action(type="apoli:if_else",
                               condition=self.to_ast(), if_action=if_action, else_action=else_action
                               )
        command = AstApoliCommand(arguments=AstChildren((action,)))
        self.runtime.commands.append(command)

    def get_path(self):
        path = self.runtime.get_nested_location().replace(":", "/functions/")
        path = f"src/data/{path}.mcfunction"
        path = path.replace("/", "\\")
        return path


# this is necessary for catching the if and else body commands
# using the bolt-control-flow mechanism
@dataclass
class ActionIfElseCase(WrappedCases):
    ctx: Context = field(repr=False)

    if_commands: AstChildren[AstCommand] = AstChildren()
    else_commands: AstChildren[AstCommand] = AstChildren()

    @contextmanager
    def __case__(self, case: Case):
        runtime = self.ctx.inject(Runtime)

        with runtime.scope() as cmds:
            yield CaseResult.maybe()

        commands = AstChildren(cmds)

        if case:
            self.if_commands = commands
        else:
            self.else_commands = commands


@dataclass
class BaseType:
    ctx: Context

    def emit_apoli_action(self, action: AstApoliAction):
        runtime = self.ctx.inject(Runtime)
        command = AstApoliCommand(arguments=AstChildren((action,)))
        runtime.commands.append(command)


@dataclass
class Resource:
    ctx: Context
    id: str

    # region Resource Equalities
    def create_comparison(self, comparison, compare_to):
        if isinstance(compare_to, int):
            return create_condition(ctx=self.ctx, type="apoli:resource", resource=self.id, comparison=comparison,
                                    compare_to=compare_to)

    def __eq__(self, other):
        return self.create_comparison(comparison="==", compare_to=other)

    def __ne__(self, other):
        return self.create_comparison(comparison="!=", compare_to=other)

    def __lt__(self, other):
        return self.create_comparison(comparison="<", compare_to=other)

    def __le__(self, other):
        return self.create_comparison(comparison="<=", compare_to=other)

    def __gt__(self, other):
        return self.create_comparison(comparison=">", compare_to=other)

    def __ge__(self, other):
        return self.create_comparison(comparison=">=", compare_to=other)
    # endregion


class PowerPhase(Enum):
    RISING = "rising_action"
    FALLING = "falling_action"
    CONSTANT = "entity_aciton"


class ShapeType(Enum):
    COLLIDER = "collider"
    OUTLINE = "outline"
    VISUAL = "visual"


class FluidHandling(Enum):
    ANY = "any"
    NONE = "none"
    SOURCE_ONLY = "source_only"


class Space(Enum):
    WORLD = "world"
    LOCAL = "local"
    LOCAL_HORIZONTAL = "local_horizontal"
    LOCAL_HORIZONTAL_NORMALIZED = "local_horizontal_normalized"
    VELOCITY = "velocity"
    VELOCITY_NORMALIZED = "velocity_normalized"
    VELOCITY_HORIZONTAL = "velocity_horizontal"
    VELOCITY_HORIZONTAL_NORMALIZED = "velocity_horizontal_normalized"


class ActionOverTimePower(BaseType):
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.runtime = self.ctx.inject(Runtime)

    def get_phase(self):
        return self

    def __eq__(self, other):
        return create_condition(ctx=self.ctx, type="internal:phase_value", phase_value=other.value)

    def __ne__(self, other):
        return create_condition(ctx=self.ctx, type="internal:phase_value", phase_value=other.value)


class MetaUtils(BaseType):
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.runtime = self.ctx.inject(Runtime)

    @contextmanager
    def sleep(self, ticks: int):
        with self.runtime.scope() as cmds:
            yield True
        self.emit_apoli_action(create_action(type="apoli:delay", ticks=ticks, action=unwrap_action(AstChildren(cmds))))


class Raycast(BaseType):
    bientity_pair: "BiEntityPair"

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.runtime = self.ctx.inject(Runtime)
        self.set_shape_type()
        self.set_fluid_handling()
        self.set_space()
        self.set_direction()
        self.bientity_pair = BiEntityPair(self.ctx)
        self.bientity_action_v = None

    def create(self, distance: float, block: bool = True, entity: bool = True):
        self.distance = distance
        self.block = block
        self.entity = entity
        return self

    def set_shape_type(self, shape_type: ShapeType = ShapeType.VISUAL):
        self.shape_type = shape_type
        return self

    def set_fluid_handling(self, fluid_handling: FluidHandling = FluidHandling.ANY):
        self.fluid_handling = fluid_handling
        return self

    def set_space(self, space: Space = Space.WORLD):
        self.space = space
        return self

    def set_direction(self, direction: Tuple[float, float, float] = None):
        self.direction = direction
        return self

    @contextmanager
    def bientity_action(self):
        with self.runtime.scope() as cmds:
            yield self.bientity_pair
        self.bientity_action_v = unwrap_action(AstChildren(cmds))
        return unwrap_action(AstChildren(cmds))

    def fire(self):
        direction = {}
        if self.direction is not None:
            direction["direction"] = self.direction

        bientity_action_v = {}
        if self.bientity_action_v is not None:
            bientity_action_v["bientity_action"] = self.bientity_action_v
        return self.emit_apoli_action(
            create_action(type="apoli:raycast", distance=self.distance, block=self.block, entity=self.entity,
                          shape_type=self.shape_type.value, fluid_handling=self.fluid_handling.value,
                          space=self.space.value, **bientity_action_v, **direction))


@dataclass
class Item(BaseType):
    ctx: Context
    equipment_slot: EquipmentSlot
    entity: "Entity"

    def get_amount(self):
        return self

    def damage(self, amount: int = 1, ignore_unbreaking: bool = False):
        return self.entity.equipped_item_action(equipment_slot=self.equipment_slot.value,
                                                action=create_action(type="apoli:damage", amount=amount,
                                                                     ignore_unbreaking=ignore_unbreaking))

    # region Item Equalities
    def create_comparison(self, comparison, compare_to):
        if isinstance(compare_to, int):
            return create_condition(ctx=self.ctx, type="apoli:amount", comparison=comparison, compare_to=compare_to)

    def create_equipped_condition(self, item_condition):
        return create_condition(ctx=self.ctx, type="apoli:equipped_item", equipment_slot=self.equipment_slot,
                                item_condition=item_condition)

    def __eq__(self, compare_to):
        if isinstance(compare_to, int):
            return self.create_equipped_condition(
                item_condition=self.create_comparison(comparison="==", compare_to=compare_to))

    def __ne__(self, compare_to):
        if isinstance(compare_to, int):
            return self.create_equipped_condition(
                item_condition=self.create_comparison(comparison="!=", compare_to=compare_to))

    def __lt__(self, compare_to):
        if isinstance(compare_to, int):
            return self.create_equipped_condition(
                item_condition=self.create_comparison(comparison="<", compare_to=compare_to))

    def __le__(self, compare_to):
        if isinstance(compare_to, int):
            return self.create_equipped_condition(
                item_condition=self.create_comparison(comparison="<=", compare_to=compare_to))

    def __gt__(self, compare_to):
        if isinstance(compare_to, int):
            return self.create_equipped_condition(
                item_condition=self.create_comparison(comparison=">", compare_to=compare_to))

    def __ge__(self, compare_to):
        if isinstance(compare_to, int):
            return self.create_equipped_condition(
                item_condition=self.create_comparison(comparison=">=", compare_to=compare_to))
    # endregion


@dataclass
class Block(BaseType):
    ctx: Context

    def is_in_tag(self, tag: str):
        return create_condition(ctx=self.ctx, type="apoli:in_tag", tag=tag)


@dataclass
class Entity(BaseType):
    ctx: Context

    def is_sneaking(self):
        return create_condition(ctx=self.ctx, type="apoli:sneaking")

    def is_on_fire(self):
        return create_condition(ctx=self.ctx, type="apoli:on_fire")

    def has_status_effect(self, effect: str, min_amplifier: int = 0, max_amplifier: int = 2147483647,
                          min_duration: int = 0, max_duration: int = 2147483647):
        return create_condition(ctx=self.ctx, type="apoli:status_effect", effect=effect, min_amplifier=min_amplifier,
                                max_amplifier=max_amplifier, min_duration=min_duration, max_duration=max_duration)

    def evaluate_command(self, command: str, comparison: str, compare_to: int):
        return create_condition(ctx=self.ctx, type="apoli:command", command=command, compare_to=compare_to,
                                comparison=comparison)

    def get_item(self, equipment_slot: EquipmentSlot):
        return Item(self.ctx, equipment_slot=equipment_slot, entity=self)

    def get_resource_value(self, id: str):
        return Resource(self.ctx, id)

    def set_resource_value(self, id: str, change: int, emit: bool = True):
        action = create_action(type="apoli:change_resource", resource=id, change=change, operation="set")
        if emit:
            self.emit_apoli_action(action)
        return action

    def add_resource_value(self, id: str, change: int, emit: bool = True):
        action = create_action(type="apoli:change_resource", resource=id, change=change, operation="add")
        if emit:
            self.emit_apoli_action(action)
        return action

    def trigger_cooldown(self, power: str, emit: bool = True):
        action = create_action(type="apoli:trigger_cooldown", power=power)
        if emit:
            self.emit_apoli_action(action)
        return action

    def equipped_item_action(self, equipment_slot, action, emit: bool = True):
        action = create_action(type="apoli:equipped_item_action", equipment_slot=equipment_slot, action=action)
        if emit:
            self.emit_apoli_action(action)
        return action

    def apply_effect(self, effect: str, duration: int = 100, amplifier: int = 0, is_ambient: bool = False,
                     show_particles: bool = True, show_icon: bool = True, emit: bool = True):
        action = create_action(type="apoli:apply_effect",
                               effect={"effect": effect, "duration": duration, "amplifier": amplifier,
                                       "is_ambient": is_ambient, "show_particles": show_particles,
                                       "show_icon": show_icon})
        if emit:
            self.emit_apoli_action(action)
        return action


class ActorTargetEntity(Entity):
    entity_type: str

    def __init__(self, ctx, entity_type):
        self.ctx = ctx
        self.entity_type = entity_type
        super().__init__(ctx=self.ctx)

    def is_sneaking(self):
        return create_condition(ctx=self.ctx, type=f"apoli:{self.entity_type}_condition",
                                condition=super().is_sneaking())

    def is_on_fire(self):
        return create_condition(ctx=self.ctx, type=f"apoli:{self.entity_type}_condition",
                                condition=super().is_on_fire())

    def has_status_effect(self, effect: str, min_amplifier: int = 0, max_amplifier: int = 2147483647,
                          min_duration: int = 0, max_duration: int = 2147483647):
        return create_condition(ctx=self.ctx, type=f"apoli:{self.entity_type}_condition",
                                condition=super().has_status_effect(effect=effect, min_amplifier=min_amplifier,
                                                                    max_amplifier=max_amplifier,
                                                                    min_duration=min_duration,
                                                                    max_duration=max_duration))

    def evaluate_command(self, command: str, comparison: str, compare_to: int):
        return create_condition(ctx=self.ctx, type=f"apoli:{self.entity_type}_condition",
                                condition=super().evaluate_command(command=command, compare_to=compare_to,
                                                                   comparison=comparison))

    def get_item(self, equipment_slot: EquipmentSlot):
        return Item(self.ctx, equipment_slot=equipment_slot, entity=self)

    def get_resource_value(self, id: str):
        return Resource(self.ctx, id)

    def set_resource_value(self, id: str, change: int, emit: bool = True):
        action = create_action(type=f"apoli:{self.entity_type}_action",
                               action=super().add_resource_value(id=id, change=change))
        return self.emit_apoli_action(action)

    def add_resource_value(self, id: str, change: int, emit: bool = True):
        action = create_action(type=f"apoli:{self.entity_type}_action",
                               action=super().add_resource_value(id=id, change=change))
        if emit:
            self.emit_apoli_action(action)
        return action

    def trigger_cooldown(self, power: str, emit: bool = True):
        action = create_action(type=f"apoli:{self.entity_type}_action", action=super().trigger_cooldown(power=power))
        if emit:
            self.emit_apoli_action(action)
        return action

    def equipped_item_action(self, equipment_slot, action, emit: bool = True):
        action = create_action(type=f"apoli:{self.entity_type}_action",
                               action=super().equipped_item_action(equipment_slot, action, emit=False))
        if emit:
            self.emit_apoli_action(action)
        return action

    def apply_effect(self, effect: str, duration: int = 100, amplifier: int = 0, is_ambient: bool = False,
                     show_particles: bool = True, show_icon: bool = True, emit: bool = True):
        action = create_action(type=f"apoli:{self.entity_type}_action",
                               action=super().apply_effect(effect=effect, duration=duration, amplifier=amplifier,
                                                           is_ambient=is_ambient, show_particles=show_particles,
                                                           show_icon=show_icon))
        if emit:
            self.emit_apoli_action(action)
        return action


class BiEntityPair(BaseType):
    ctx: Context
    actor: ActorTargetEntity
    target: ActorTargetEntity

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.runtime = self.ctx.inject(Runtime)
        self.actor = ActorTargetEntity(self.ctx, "actor")
        self.target = ActorTargetEntity(self.ctx, "target")

    def get_actor(self):
        return self.actor

    def get_target(self):
        return self.target

    def add_to_set(self, set: str, time_limit: Optional[int], emit: bool = True):
        time_limit_d = {}
        if time_limit is not None:
            time_limit_d["time_limit"] = time_limit
        action = create_action(type="apoli:add_to_set", set=set, **time_limit_d)
        if emit:
            self.emit_apoli_action(action)
        return action

    def add_velocity(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, reference: str = "position",
                     client: bool = True, server: bool = True, set: bool = False, emit: bool = True):
        action = create_action(type="apoli:add_velocity", x=x, y=y, z=z, reference=reference, client=client,
                               server=server, set=set)
        if emit:
            self.emit_apoli_action(action)
        return action

    def damage(self, amount: float, damage_type: str, modifier, modifiers, emit: bool = True):
        modifier_d = {}
        if modifier is not None:
            modifier_d["modifier"] = modifier
        modifiers_d = {}
        if modifiers is not None:
            modifiers_d["modifiers"] = modifiers
        action = create_action(type="apoli:damage", amount=amount, damage_type=damage_type, modifier=modifier_d,
                               modifiers=modifiers_d)
        if emit:
            self.emit_apoli_action(action)
        return action

    def mount(self, emit: bool = True):
        action = create_action(type="apoli:mount")
        if emit:
            self.emit_apoli_action(action)
        return action

    def remove_from_set(self, set: str, emit: bool = True):
        action = create_action(type="apoli:remove_from_set", set=set)
        if emit:
            self.emit_apoli_action(action)
        return action

    def set_in_love(self, emit: bool = True):
        action = create_action(type="apoli:set_in_love")
        if emit:
            self.emit_apoli_action(action)
        return action

    def tame(self, emit: bool = True):
        action = create_action(type="apoli:tame")
        if emit:
            self.emit_apoli_action(action)
        return action


# this class implements the power decorator functionality
# decorating a function with 'power' calls the function immediately,
# wrapping the produced commands into a AstApoliPowerCommand node
# that gets transformed later
@dataclass
class Power:
    ctx: Context

    @property
    def runtime(self):
        return self.ctx.inject(Runtime)

    def decorate(self, type_field: str, path: str | None, name, description, condition, fields, f: Callable[[], None]):
        # generate default path if not provided
        if path is None:
            pname = f.__name__
            path = self.ctx.generate.path(pname)

        # collect commands generated from the function
        with self.runtime.scope() as cmds:
            if type_field == "apoli:action_over_time":
                f(ActionOverTimePower(ctx=self.ctx))
            else:
                f()

        file_subname = path.split(":")[1]
        file_name = self.runtime.get_nested_location()

        new_cmds = []
        for cmd in cmds:
            new_cmd_arguments = []
            for argument in cmd.arguments:
                if isinstance(argument, AstApoliAction) and argument.type.startswith("internal:"):
                    continue

                new_cmd_arguments.append(argument)
            if len(new_cmd_arguments) > 0:
                if isinstance(cmd, AstApoliCommand):
                    new_cmd = AstApoliCommand(identifier=cmd.identifier, arguments=AstChildren((*new_cmd_arguments,)))
                else:
                    new_cmd = AstCommand(identifier=cmd.identifier, arguments=AstChildren((*new_cmd_arguments,)))
                new_cmds.append(new_cmd)

        entity_action = unwrap_action(AstChildren(cmds))
        if entity_action is not None:
            if entity_action.type == "apoli:and":
                for action in entity_action.fields[0].value.value:
                    if action.fields[0].value.key.startswith("internal:") and isinstance(action, AstApoliAction):
                        # if isinstance(entity_action.fields[0].value, AstApoliField):
                        #    fields[entity_action.fields[0].value.key] = entity_action.fields[0].value.value
                        # elif isinstance(entity_action.fields[0].value, AstApoliAction):
                        #    fields[entity_action.fields[0].key] = entity_action.fields[0].value
                        fields[action.fields[0].value.key] = action.fields[0].value.value
            elif entity_action.type.startswith("internal:") and isinstance(entity_action, AstApoliAction):
                if isinstance(entity_action.fields[0].value, AstApoliField):
                    fields[entity_action.fields[0].value.key] = entity_action.fields[0].value.value
                elif isinstance(entity_action.fields[0].value, AstApoliAction):
                    fields[entity_action.fields[0].key] = entity_action.fields[0].value

            entity_action = unwrap_action(AstChildren(new_cmds))
            if entity_action is not None:
                fields["entity_action"] = entity_action

        power = create_power(file_name=file_name, file_subname=file_subname, type=type_field, condition=condition,
                             name=name, description=description, **fields)
        command = AstApoliPowerCommand(resource_location=path, arguments=AstChildren((power,)))
        self.runtime.commands.append(command)
        return f

    def __call__(self, type: str, path: str | None = None, condition: Condition | None = None, name: str | AstJson = "",
                 description: str | AstJson = "", **fields: Any):
        return partial(self.decorate, type, path, name, description, condition, fields)


def create_multiple(type: str, **fields: Any) -> AstApoliMultiplePower:
    ast_fields = AstChildren(
        AstApoliField(
            key=key,
            value=AstApoliLiteral(value=value)
            if not isinstance(value, AstNode)
            else value,
        )
        for key, value in fields.items()
    )
    file_name, file_subname, name, description = "", "", "", ""
    element = list(fields.items())[0][1]
    if isinstance(element, AstChildren):
        for child in element:
            for power in child:
                if isinstance(power, AstApoliPower):
                    file_name, file_subname, name, description = power.file_name, power.file_subname, power.name, power.description
    return AstApoliMultiplePower(type=type, file_name=file_name, file_subname=file_subname, name=name,
                                 description=description, condition=None, fields=ast_fields)


def create_power(file_name: str, file_subname: str, type: str, name, description, condition=None,
                 **fields: Any) -> AstApoliPower:
    ast_fields = AstChildren(
        AstApoliField(
            key=key,
            value=AstApoliLiteral(value=value)
            if not isinstance(value, AstNode)
            else value,
        )
        for key, value in fields.items()
    )
    return AstApoliPower(file_name=file_name, file_subname=file_subname, type=type, name=name, description=description,
                         condition=condition, fields=ast_fields)


# region Transformer
@dataclass
class ApoliTransformer(MutatingReducer):
    """
    Transformer for Apoli commands.

    Traverses the child commands of nested root, filters out Apoli commands
    and emits power resource files.
    """

    generate: BeetGenerator = required_field()
    pack: DataPack = required_field()
    converter: "ApoliJsonConverter" = required_field()

    @rule(AstRoot)
    def apoli_command(self, node: AstRoot) -> Generator[Any, Any, Any]:
        commands: list[AstCommand] = []
        changed = False
        power_asts = []

        for command in node.commands:
            # don't touch commands that are not from this plugin
            if not isinstance(command, AstApoliCommand):
                commands.append(command)
                continue

            # prevent the user from using apoli actions in functions/command roots.
            # the error location is not precise though
            #
            # if possible, this could actually produce some anonymous power and
            # directly up trigger it using a command, kinda like how anonymous functions work
            if not isinstance(command, AstApoliPowerCommand):
                yield set_location(
                    Diagnostic("error", "Invalid Apoli command outside of power root."),
                    location=node.location,
                    end_location=node.location,
                )
                continue

            changed = True
            if len(node.commands) > 1:
                power_ast = command.arguments[0]
                if not isinstance(power_ast, AstApoliMultiplePower):
                    power_asts.append(power_ast)
            else:
                power_ast = command.arguments[0]
                json = self.converter(power_ast)
                namespace, path = power_ast.file_name.split(":")
                path = np.char.rpartition(path, '/')[0]
                power_id = f"{namespace}:{path}/{command.resource_location.split(':')[1]}"
                self.generate(power_id, PowerFile(json))
            # generates a power file at the specified location
            # with the generated json as contents

        if len(power_asts) > 0:
            power_metadata = power_asts[0]
            if isinstance(power_metadata, AstApoliPower) and not isinstance(power_metadata, AstApoliMultiplePower):
                power_ast = create_multiple(type="apoli:multiple", fields=AstChildren((power_asts,)))
                json = self.converter(power_ast)
                self.generate(power_ast.file_name, PowerFile(json))
        if changed:
            node = replace(node, commands=AstChildren(commands))
        return node


# endregion

# region Json Converter
@dataclass
class ApoliJsonConverter(Visitor):
    """Converts Apoli AST to JSON."""

    serialize: Serializer = required_field()

    def build_dict(self, node: AstApoliTypedObject):
        base_dict = {"type": node.type}
        for field in node.fields:
            if isinstance(field, AstApoliField):
                if isinstance(field.value, AstCommand):
                    base_dict[field.key] = self.serialize(field.value)
                elif isinstance(field.value, AstApoliLiteral):
                    base_dict[field.key] = self.literal(self, field.value)
                elif isinstance(field.value, AstApoliTypedObject):
                    base_dict[field.key] = self.build_dict(field.value)
                elif isinstance(field.value, AstApoliField):
                    base_dict[field.value.key] = self.build_dict(field.value.value)
                else:
                    base_dict[field.key] = field.value
        return base_dict

    @rule(AstApoliMultiplePower)
    def multiple_power(self, node: AstApoliMultiplePower) -> Generator[AstNode, Any, Any]:
        base_power = {"type": node.type}
        # base_power = self.build_dict(node)
        name, description = "", ""
        for child in node.fields:
            if isinstance(child, AstApoliField):
                if isinstance(child.value, AstApoliLiteral):
                    for power in child.value.value:
                        for subpower in power:
                            if isinstance(subpower, AstApoliPower):
                                base_power[subpower.file_subname] = self.build_dict(subpower)
                                if subpower.condition is not None:
                                    if isinstance(subpower.condition, AstApoliCondition):
                                        condition = yield subpower.condition
                                    elif isinstance(subpower.condition, Condition):
                                        condition = yield subpower.condition.to_ast()
                                    base_power[subpower.file_subname]["condition"] = condition
                                if name == "" and description == "":
                                    name, description = subpower.name, subpower.description
        if name == "" and description == "":
            base_power["hidden"] = True
        if name != "":
            base_power["name"] = name
        if description != "":
            base_power["description"] = description
        return base_power

    @rule(AstApoliPower)
    def power(self, node: AstApoliPower) -> Generator[AstNode, Any, Any]:
        base_power = self.build_dict(node)
        if node.condition is not None:
            condition = yield node.condition.to_ast()
            if condition is not None:
                base_power["condition"] = condition
        if node.name == "" and node.description == "":
            base_power["hidden"] = True
        if node.name != "":
            base_power["name"] = node.name
        if node.description != "":
            base_power["description"] = node.description
        return base_power

    @rule(AstApoliAction)
    def action(self, node: AstApoliAction) -> Any:
        base_action = self.build_dict(node)
        return base_action

    @rule(AstApoliCondition)
    def condition(self, node: AstApoliCondition) -> Any:
        base_condition = self.build_dict(node)
        if node.inverted:
            base_condition["inverted"] = True
        return base_condition

    @rule(AstApoliLiteral)
    def literal(self, node: AstApoliLiteral) -> Any:
        values = []
        if isinstance(node.value, AstChildren):
            for child in node.value:
                if isinstance(child, AstApoliAction):
                    values.append(self.action(self, child))
                if isinstance(child, AstApoliCondition):
                    values.append(self.condition(self, child))
        elif isinstance(node.value, EquipmentSlot):
            values = node.value.value
        elif isinstance(node.value, List):
            for value in node.value:
                if isinstance(value, AstApoliCondition):
                    values.append(self.condition(self, value))
        elif isinstance(node.value, AstApoliCondition):
            values.append(self.condition(self, node.value))
        elif isinstance(node.value, Condition):
            values = self.condition(self, node.value.to_ast())
        else:
            values = node.value
        return values

# endregion