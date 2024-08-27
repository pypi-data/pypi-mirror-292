import { DocumentRegistry, DocumentWidget, DocumentModel } from '@jupyterlab/docregistry';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { SplitPanel } from '@lumino/widgets';
import { BlocklyManager } from './manager';
import { CodeCell } from '@jupyterlab/cells';
import { IEditorFactoryService } from '@jupyterlab/codeeditor';
/**
 * DocumentWidget: widget that represents the view or editor for a file type.
 */
export declare class BlocklyEditor extends DocumentWidget<BlocklyPanel, DocumentModel> {
    constructor(options: BlocklyEditor.IOptions);
    /**
     * Dispose of the resources held by the widget.
     */
    dispose(): void;
}
export declare namespace BlocklyEditor {
    interface IOptions extends DocumentWidget.IOptions<BlocklyPanel, DocumentModel> {
        manager: BlocklyManager;
    }
}
/**
 * Widget that contains the main view of the DocumentWidget.
 */
export declare class BlocklyPanel extends SplitPanel {
    private _context;
    private _rendermime;
    /**
     * Construct a `BlocklyPanel`.
     *
     * @param context - The documents context.
     */
    constructor(context: DocumentRegistry.IContext<DocumentModel>, manager: BlocklyManager, rendermime: IRenderMimeRegistry, factoryService: IEditorFactoryService);
    get cell(): CodeCell;
    get rendermime(): IRenderMimeRegistry;
    /**
     * Dispose of the resources held by the widget.
     */
    dispose(): void;
    private _load;
    private _onSave;
}
