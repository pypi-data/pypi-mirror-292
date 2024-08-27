import { DocumentWidget } from '@jupyterlab/docregistry';
import { runIcon } from '@jupyterlab/ui-components';
import { SplitPanel } from '@lumino/widgets';
import { Signal } from '@lumino/signaling';
import { BlocklyLayout } from './layout';
import { BlocklyButton, SelectGenerator, SelectToolbox, Spacer } from './toolbar';
/**
 * DocumentWidget: widget that represents the view or editor for a file type.
 */
export class BlocklyEditor extends DocumentWidget {
    constructor(options) {
        super(options);
        // Loading the ITranslator
        // const trans = this.translator.load('jupyterlab');
        // Create and add a button to the toolbar to execute
        // the code.
        const button = new BlocklyButton({
            label: '',
            icon: runIcon,
            className: 'jp-blockly-runButton',
            onClick: () => this.content.layout.run(),
            tooltip: 'Run Code'
        });
        this.toolbar.addItem('run', button);
        this.toolbar.addItem('spacer', new Spacer());
        this.toolbar.addItem('toolbox', new SelectToolbox({
            label: 'Toolbox',
            tooltip: 'Select tollbox',
            manager: options.manager
        }));
        this.toolbar.addItem('generator', new SelectGenerator({
            label: 'Kernel',
            tooltip: 'Select kernel',
            manager: options.manager
        }));
    }
    /**
     * Dispose of the resources held by the widget.
     */
    dispose() {
        this.content.dispose();
        super.dispose();
    }
}
/**
 * Widget that contains the main view of the DocumentWidget.
 */
export class BlocklyPanel extends SplitPanel {
    /**
     * Construct a `BlocklyPanel`.
     *
     * @param context - The documents context.
     */
    constructor(context, manager, rendermime, factoryService) {
        super({
            layout: new BlocklyLayout(manager, context.sessionContext, rendermime, factoryService)
        });
        this.addClass('jp-BlocklyPanel');
        this._context = context;
        this._rendermime = rendermime;
        // Load the content of the file when the context is ready
        this._context.ready.then(() => this._load());
        // Connect to the save signal
        this._context.saveState.connect(this._onSave, this);
    }
    /*
     * The code cell.
     */
    get cell() {
        return this.layout.cell;
    }
    /*
     * The rendermime instance used in the code cell.
     */
    get rendermime() {
        return this._rendermime;
    }
    /**
     * Dispose of the resources held by the widget.
     */
    dispose() {
        if (this.isDisposed) {
            return;
        }
        Signal.clearData(this);
        super.dispose();
    }
    _load() {
        // Loading the content of the document into the workspace
        const content = this._context.model.toJSON();
        this.layout.workspace = content;
    }
    _onSave(sender, state) {
        if (state === 'started') {
            const workspace = this.layout.workspace;
            this._context.model.fromJSON(workspace);
        }
    }
}
//# sourceMappingURL=widget.js.map