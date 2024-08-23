from typing import Any, Literal, NewType, TypedDict, Union
CommonStr = NewType('CommonStr', str)


class Schema(TypedDict):
    T: Literal['F', 'D']
    B: bytes
    P: dict[str, 'Schema']


class Wflow(TypedDict):
    WFWorkflowMinimumClientVersionString: str
    WFWorkflowMinimumClientVersion: int
    WFWorkflowIcon: 'WfworkflowiconDict'
    WFWorkflowClientVersion: str
    WFWorkflowActions: list[Union['CommonAction', 'WFArchiveAction']]
    WFWorkflowHasOutputFallback: bool
    WFWorkflowOutputContentItemClasses: list
    WFWorkflowInputContentItemClasses: list[str]
    WFWorkflowImportQuestions: list
    WFWorkflowTypes: list[str]
    WFQuickActionSurfaces: list
    WFWorkflowHasShortcutInputVariables: bool

    class WfworkflowiconDict(TypedDict):
        WFWorkflowIconStartColor: int
        WFWorkflowIconGlyphNumber: int

    class CommonAction(TypedDict):
        WFWorkflowActionIdentifier: CommonStr
        WFWorkflowActionParameters: dict[str, Any]

    class WFArchiveAction(TypedDict):
        WFWorkflowActionIdentifier: Literal['is.workflow.actions.wfarchive']
        WFWorkflowActionParameters: Schema


class Record(TypedDict):
    fields: 'FieldsDict'
    modified: 'ModifiedDict'
    recordType: str
    deleted: bool
    recordChangeTag: str
    recordName: str
    pluginFields: dict
    created: 'CreatedDict'

    class FieldsDict(TypedDict):
        icon_glyph: 'Icon_glyphDict'
        signingCertificateExpirationDate: 'SigningcertificateexpirationdateDict'
        signingStatus: 'SigningstatusDict'
        shortcut: 'ShortcutDict'
        icon_color: 'Icon_colorDict'
        signedShortcut: 'SignedshortcutDict'
        icon: 'IconDict'
        maliciousScanningContentVersion: 'MaliciousscanningcontentversionDict'
        name: 'NameDict'

        class Icon_glyphDict(TypedDict):
            value: int
            type: str

        class SigningcertificateexpirationdateDict(TypedDict):
            value: int
            type: str

        class SigningstatusDict(TypedDict):
            type: str
            value: str

        class ShortcutDict(TypedDict):
            type: str
            value: 'ValueDict'

            class ValueDict(TypedDict):
                downloadURL: str
                fileChecksum: str
                size: int

        class Icon_colorDict(TypedDict):
            value: int
            type: str

        class SignedshortcutDict(TypedDict):
            value: 'ValueDict'
            type: str

            class ValueDict(TypedDict):
                downloadURL: str
                fileChecksum: str
                size: int

        class IconDict(TypedDict):
            type: str
            value: 'ValueDict'

            class ValueDict(TypedDict):
                size: int
                downloadURL: str
                fileChecksum: str

        class MaliciousscanningcontentversionDict(TypedDict):
            type: str
            value: int

        class NameDict(TypedDict):
            value: str
            type: str

    class ModifiedDict(TypedDict):
        deviceID: str
        timestamp: int
        userRecordName: str

    class CreatedDict(TypedDict):
        userRecordName: str
        deviceID: str
        timestamp: int
