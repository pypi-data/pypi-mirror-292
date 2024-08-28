"""
    Entities corresponding to Kafka messages defined with AVRO schemas for JAWS.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Union, Optional, List
from functools import total_ordering

class AlarmPriority(Enum):
    """
        Alarm Priority
    """
    P1_CRITICAL = 1
    P2_MAJOR = 2
    P3_MINOR = 3
    P4_INCIDENTAL = 4


class UnionEncoding(Enum):
    """
        Enum of possible ways to encode an AVRO union instance in Python.
    """
    TUPLE = 1
    """Instance is a two-tuple of (str - type name, dict); this is how fastavro works (
    https://fastavro.readthedocs.io/en/latest/writer.html#using-the-tuple-notation-to-specify-which-branch-of-a-union
    -to-take) """
    DICT_WITH_TYPE = 2
    """Instance is a dict with one entry of key type name str and value dict; this serializes to JSON as AVRO expects
    (except for logical types and bytes) - See:  http://avro.apache.org/docs/current/spec.html#json_encoding"""
    POSSIBLY_AMBIGUOUS_DICT = 3
    """Instance dict provided without type name - which in the case of records with identical fields there is no way
    to determine which is which (example: union of classes A and B where each has identical fields)"""


class AlarmState(Enum):
    """
        Alarm State
    """
    NormalDisabled = 1
    """Effectively Normal, out-of-service"""
    NormalFiltered = 2
    """Effectively Normal, suppressed by design"""
    NormalMasked = 3
    """Effectively Normal, hidden by parent alarm"""
    NormalOnDelayed = 4
    """Effectively Normal, temporarily suppressed upon activation"""
    NormalOneShotShelved = 5
    """Effectively Normal, temporarily suppressed until next deactivation or expiration"""
    NormalContinuousShelved = 6
    """Effectively Normal, temporarily suppressed until expiration"""
    ActiveOffDelayed = 7
    """Effectively Active, temporarily incited upon deactivation"""
    ActiveLatched = 8
    """Effectively Active, temporarily incited upon activation"""
    Active = 9
    """Effectively Active, Actually Active, timely operator action required"""
    Normal = 10
    """Effectively Normal, Actually Normal, no action required"""


@total_ordering
class OverriddenAlarmType(Enum):
    """
        Override Type
    """
    Disabled = 1
    """A broken alarm can be flagged as out-of-service"""
    Filtered = 2
    """An alarm can be "suppressed by design" - generally a group of alarms are filtered out when not needed for the
    current machine program. The Filter Processor helps operators filter multiple alarms with simple grouping
    commands (like by area)."""
    Masked = 3
    """An alarm can be suppressed by a parent alarm to minimize confusion during an alarm flood and build an
    alarm hierarchy"""
    OnDelayed = 4
    """An alarm with an on-delay is temporarily suppressed upon activation to minimize fleeting/chattering"""
    OffDelayed = 5
    """An alarm with an off-delay is temporarily incited upon de-activation to minimize fleeting/chattering"""
    Shelved = 6
    """An alarm can be temporarily suppressed via manual operator command"""
    Latched = 7
    """A fleeting alarm (one that toggles between active and not active too quickly) can be configured to require
    acknowledgement by operators - the alarm is latched once active and won't clear to Normal (or Active) until
    acknowledged"""

    def __lt__(self, other):
        return self.value < other.value

class ShelvedReason(Enum):
    """
        Shelve Reason
    """
    Stale_Alarm = 1
    """Nuisance alarm which remains active for an extended period of time"""
    Chattering_Fleeting_Alarm = 2
    """Nuisance alarm which toggles between active and normal states quickly (fleeting) and may do this often
    (chattering)"""
    Other = 3
    """Some other reason"""


class EPICSSEVR(Enum):
    """
        EPICS Alarm Severity
    """
    NO_ALARM = 1
    MINOR = 2
    MAJOR = 3
    INVALID = 4


class EPICSSTAT(Enum):
    """
        EPICS Alarm Status
    """
    NO_ALARM = 1
    READ = 2
    WRITE = 3
    HIHI = 4
    HIGH = 5
    LOLO = 6
    LOW = 7
    STATE = 8
    COS = 9
    COMM = 10
    TIMEOUT = 11
    HW_LIMIT = 12
    CALC = 13
    SCAN = 14
    LINK = 15
    SOFT = 16
    BAD_SUB = 17
    UDF = 18
    DISABLE = 19
    SIMM = 20
    READ_ACCESS = 21
    WRITE_ACCESS = 22


@dataclass
class AlarmSystem:
    """
        Alarm System record
    """
    team: str
    """Team name"""


@dataclass
class AlarmLocation:
    """
        Alarm Location record
    """
    parent: Optional[str]
    """Parent Location or null if top-level"""


@dataclass
class Activation:
    """
        Alarming state for a simple alarm, if record is present then alarming, but there are no additional fields.
    """


@dataclass
class NoActivation:
    """
        An explicit no activation record can be aggressively compacted in Kafka (unlike a tombstone).
    """


@dataclass
class NoteActivation:
    """
        Alarming state for an alarm with an extra information string.
    """
    note: str
    """A note containing extra information generated at the time of activation"""


@dataclass
class EPICSActivation:
    """
        EPICS alarming state.
    """
    sevr: EPICSSEVR
    """The severity"""
    stat: EPICSSTAT
    """The status"""


@dataclass
class ChannelErrorActivation:
    """
        A channel error between JAWS and an alarm activation source.
    """
    error: str
    """Description of the error such as Never Connected or Disconnected"""


@dataclass
class Source:
    """
        Base alarm source with no registered alarm-specific information.
    """


@dataclass
class EPICSSource:
    """
        EPICS source registration information.
    """
    pv: str
    """The EPICS Process Variable name"""


@dataclass
class CALCSource:
    """
        CALC Expression Alarm Generator source registration information.
    """
    expression: str
    """The CALC (calculate) expression"""


@dataclass
class DisabledOverride:
    """
        Disabled override - Suppresses an alarm that is out-of-service (usually for maintenance)
    """
    comments: Optional[str]
    """Explanation of why the alarm is out-of-service"""


@dataclass
class FilteredOverride:
    """
        Filtered override - Suppresses an alarm via filter rule
    """
    filtername: str
    """Filter rule causing the alarm to be filtered"""


@dataclass
class LatchedOverride:
    """
        Latched override - Incites an alarm until an operator acknowledgement
    """


@dataclass
class MaskedOverride:
    """
        Masked override - Suppresses an alarm when a parent alarm is active
        (establishes a hierarchy and minimizes alarm flooding)
    """


@dataclass
class OnDelayedOverride:
    """
        On-Delay override - Suppresses an alarm for a short duration upon activation
    """
    expiration: int
    """Expiration timestamp (Unix timestamp of milliseconds since Epoch of Jan 1. 1970 UTC)"""


@dataclass
class OffDelayedOverride:
    """
        Off-Delay override - Incites an alarm for a short duration upon deactivation
    """
    expiration: int
    """Expiration timestamp (Unix timestamp of milliseconds since Epoch of Jan 1. 1970 UTC)"""


@dataclass
class ShelvedOverride:
    """
        Shelved override - a temporary override (expires)
    """
    expiration: int
    """Expiration timestamp (Unix timestamp of milliseconds since Epoch of Jan 1. 1970 UTC)"""
    comments: Optional[str]
    """Additional operator comments explaining why the alarm was shelved"""
    reason: ShelvedReason
    """The general motivation for shelving the alarm"""
    oneshot: bool
    """Indicates whether the override expires immediately upon next alarm deactivation
    (unless timestamp expiration occurs first)"""


@dataclass
class AlarmAction:
    """
        Alarm Action (class of alarm)
    """
    system: str
    """The Alarm System"""
    priority: AlarmPriority
    """The Alarm Priority"""
    rationale: str
    """The Rationale"""
    corrective_action: str
    """The Corrective Action"""
    latchable: bool
    """Indicates whether the alarm latches"""
    filterable: bool
    """Indicates whether the alarm can be filtered"""
    on_delay_seconds: Optional[int]
    """(optional) The on-delay in seconds - non-positive is treated as None"""
    off_delay_seconds: Optional[int]
    """(optional) The off-delay in seconds - non-positive is treated as None"""


@dataclass
class Alarm:
    """
        Alarm registration instance.   An instance associates with action class attributes, but also brings
        instance-specific attributes.
    """
    action: str
    """The Alarm Action"""
    source: Union[Source, EPICSSource, CALCSource]
    """The Alarm Source specific info"""
    location: List[str]
    """The Alarm Location"""
    managed_by: Optional[str]
    """(optional) Whom manages this alarm"""
    masked_by: Optional[str]
    """(optional) The parent alarm which masks this one"""
    screen_command: str
    """The command to open the related control system screen"""


@dataclass
class AlarmActivationUnion:
    """
        Alarm Activation (annunciation, alarming).
    """
    union: Union[Activation, NoteActivation, EPICSActivation, ChannelErrorActivation, NoActivation]
    """The message payload is a union of possible alarming types"""


@dataclass(frozen=True)
@total_ordering
class AlarmOverrideKey:
    """
        alarm-overrides-key subject
    """
    name: str
    """The alarm name"""
    type: OverriddenAlarmType
    """The override type"""

    def __eq__(self, other):
        return ((self.name, self.type.value) ==
                (other.name, other.type.value))

    def __lt__(self, other):
        return ((self.name, self.type.value) <
                (other.name, other.type.value))

@dataclass
class AlarmOverrideUnion:
    """
        Alarm Override (a single override modeled as a union of possible types, like an enum)
    """
    union: Union[DisabledOverride, FilteredOverride, LatchedOverride, MaskedOverride, OnDelayedOverride,
                 OffDelayedOverride, ShelvedOverride]
    """The message payload is a union of possible overrides"""


@dataclass
class AlarmOverrideSet:
    """
        Set of all overrides for an alarm
    """
    disabled: DisabledOverride
    """Disabled Override"""
    filtered: FilteredOverride
    """Filtered Override"""
    latched: LatchedOverride
    """Latched Override"""
    masked: MaskedOverride
    """Masked Override"""
    ondelayed: OnDelayedOverride
    """On Delayed Override"""
    offdelayed: OffDelayedOverride
    """Off Delayed Override"""
    shelved: ShelvedOverride
    """Shelved Override"""


@dataclass
class ProcessorTransitions:
    """
        Set of transition states as alarm data is joined and processed
    """
    transition_to_active: bool
    """true when record is first one to indicate Active after being Normal"""
    transition_to_normal: bool
    """true when record is first one to indicate Normal after being Active"""
    latching: bool
    """true when record is in-process of latching, LatchOverride forthcoming"""
    unshelving: bool
    """true when record is in-process of being unshelved after one-shot, ShelvedOverride clearing"""
    masking: bool
    """true when record is in-process of being masked, MaskedOverride forthcoming"""
    unmasking: bool
    """true when record is in-process of being unmasked, MaskedOverride clearing"""
    ondelaying: bool
    """true when record is in-process of being on-delayed, OnDelayedOverride forthcoming"""
    offdelaying: bool
    """true when record is in-process of being off-delayed, OffDelayedOverride forthcoming"""


@dataclass
class EffectiveRegistration:
    """
        Effective Registration (action class + alarm instance)
    """
    action: AlarmAction
    """The Alarm Action (class of alarm)"""

    alarm: Alarm
    """The registered alarm instance"""


@dataclass
class EffectiveNotification:
    """
        Effective Notification (activation + overrides + state)
    """
    activation: AlarmActivationUnion
    """The Alarm Activation"""

    overrides: AlarmOverrideSet
    """The Alarm Overrides"""

    state: AlarmState
    """The calculated AlarmState considering activation and overrides"""


@dataclass
class EffectiveAlarm:
    """
        Effective Alarm (effective registration + effective activation)
    """
    registration: EffectiveRegistration
    """The EffectiveRegistration considering class defaults"""

    notification: EffectiveNotification
    """The EffectiveNotification considering overrides"""


@dataclass
class IntermediateMonolog:
    """
        IntermediateMonolog - used internally by the jaws-effective-processor.
    """
    registration: EffectiveRegistration
    """The effective AlarmRegistration considering class defaults"""

    notification: EffectiveNotification
    """The effective AlarmActivation considering overrides"""

    transitions: ProcessorTransitions
    """Transition states used by the alarm processor"""
