import { ABCWidgetFactory, DocumentRegistry, DocumentModel } from '@jupyterlab/docregistry';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { IEditorFactoryService, IEditorMimeTypeService } from '@jupyterlab/codeeditor';
import { BlocklyEditor } from './widget';
import { BlocklyRegistry } from './registry';
/**
 * A widget factory to create new instances of BlocklyEditor.
 */
export declare class BlocklyEditorFactory extends ABCWidgetFactory<BlocklyEditor, DocumentModel> {
    private _registry;
    private _rendermime;
    private _mimetypeService;
    private _factoryService;
    /**
     * Constructor of BlocklyEditorFactory.
     *
     * @param options Constructor options
     */
    constructor(options: BlocklyEditorFactory.IOptions);
    get registry(): BlocklyRegistry;
    /**
     * Create a new widget given a context.
     *
     * @param context Contains the information of the file
     * @returns The widget
     */
    protected createNewWidget(context: DocumentRegistry.IContext<DocumentModel>): BlocklyEditor;
}
export declare namespace BlocklyEditorFactory {
    interface IOptions extends DocumentRegistry.IWidgetFactoryOptions {
        rendermime: IRenderMimeRegistry;
        mimetypeService: IEditorMimeTypeService;
        /**
         * An editor factory service instance.
         */
        factoryService: IEditorFactoryService;
    }
}
