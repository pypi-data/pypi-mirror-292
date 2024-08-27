import {
  ABCWidgetFactory,
  DocumentRegistry,
  DocumentModel
} from '@jupyterlab/docregistry';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import {
  IEditorFactoryService,
  IEditorMimeTypeService
} from '@jupyterlab/codeeditor';

import { BlocklyEditor, BlocklyPanel } from './widget';
import { BlocklyRegistry } from './registry';
import { BlocklyManager } from './manager';

/**
 * A widget factory to create new instances of BlocklyEditor.
 */
export class BlocklyEditorFactory extends ABCWidgetFactory<
  BlocklyEditor,
  DocumentModel
> {
  private _registry: BlocklyRegistry;
  private _rendermime: IRenderMimeRegistry;
  private _mimetypeService: IEditorMimeTypeService;
  private _factoryService: IEditorFactoryService;

  /**
   * Constructor of BlocklyEditorFactory.
   *
   * @param options Constructor options
   */
  constructor(options: BlocklyEditorFactory.IOptions) {
    super(options);
    this._registry = new BlocklyRegistry();
    this._rendermime = options.rendermime;
    this._mimetypeService = options.mimetypeService;
    this._factoryService = options.factoryService;
  }

  get registry(): BlocklyRegistry {
    return this._registry;
  }

  /**
   * Create a new widget given a context.
   *
   * @param context Contains the information of the file
   * @returns The widget
   */
  protected createNewWidget(
    context: DocumentRegistry.IContext<DocumentModel>
  ): BlocklyEditor {
    // Set a map to the model. The widgets manager expects a Notebook model
    // but the only notebook property it uses is the metadata.
    context.model['metadata'] = new Map();
    const manager = new BlocklyManager(
      this._registry,
      context.sessionContext,
      this._mimetypeService
    );
    const content = new BlocklyPanel(
      context,
      manager,
      this._rendermime,
      this._factoryService
    );
    return new BlocklyEditor({ context, content, manager });
  }
}

export namespace BlocklyEditorFactory {
  export interface IOptions extends DocumentRegistry.IWidgetFactoryOptions {
    /*
     * A rendermime instance.
     */
    rendermime: IRenderMimeRegistry;
    /*
     * A mimeType service instance.
     */
    mimetypeService: IEditorMimeTypeService;
    /**
     * An editor factory service instance.
     */
    factoryService: IEditorFactoryService;
  }
}
