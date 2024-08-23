from . import typing
record_url = 'https://www.icloud.com/shortcuts/api/records/%s'


def wflow(schema: typing.Schema):
    return {
        'WFWorkflowMinimumClientVersionString': '900',
        'WFWorkflowMinimumClientVersion': 900,
        'WFWorkflowIcon': {
            'WFWorkflowIconStartColor': 2846468607,
            'WFWorkflowIconGlyphNumber': 59653
        },
        'WFWorkflowClientVersion': '2206.0.5',
        'WFWorkflowActions': [
            {
                'WFWorkflowActionIdentifier': 'is.workflow.actions.comment',
                'WFWorkflowActionParameters': {
                    'WFCommentActionText': 'This workflow is not intended for human readability.'
                }
            },
            {
                'WFWorkflowActionIdentifier': 'is.workflow.actions.wfarchive',
                'WFWorkflowActionParameters': schema
            }
        ],
        'WFWorkflowHasOutputFallback': False,
        'WFWorkflowOutputContentItemClasses': [],
        'WFWorkflowInputContentItemClasses': [
            'WFAppContentItem',
            'WFAppStoreAppContentItem',
            'WFArticleContentItem',
            'WFContactContentItem',
            'WFDateContentItem',
            'WFEmailAddressContentItem',
            'WFFolderContentItem',
            'WFGenericFileContentItem',
            'WFImageContentItem',
            'WFiTunesProductContentItem',
            'WFLocationContentItem',
            'WFDCMapsLinkContentItem',
            'WFAVAssetContentItem',
            'WFPDFContentItem',
            'WFPhoneNumberContentItem',
            'WFRichTextContentItem',
            'WFSafariWebPageContentItem',
            'WFStringContentItem',
            'WFURLContentItem'
        ],
        'WFWorkflowImportQuestions': [],
        'WFWorkflowTypes': ['Watch'],
        'WFQuickActionSurfaces': [],
        'WFWorkflowHasShortcutInputVariables': False
    }
