import { showErrorMessage } from '@jupyterlab/apputils';
import { Cell, CodeCell, CodeCellModel } from '@jupyterlab/cells';
import { SplitLayout, SplitPanel, Widget } from '@lumino/widgets';
import { Signal } from '@lumino/signaling';
import * as Blockly from 'blockly';
import { THEME } from './utils';
/**
 * A blockly layout to host the Blockly editor.
 */
export class BlocklyLayout extends SplitLayout {
    /**
     * Construct a `BlocklyLayout`.
     *
     */
    constructor(manager, sessionContext, rendermime, factoryService) {
        super({ renderer: SplitPanel.defaultRenderer, orientation: 'vertical' });
        this._manager = manager;
        this._sessionContext = sessionContext;
        // Creating the container for the Blockly editor
        // and the output area to render the execution replies.
        this._host = new Widget();
        // Creating a CodeCell widget to render the code and
        // outputs from the execution reply.
        this._cell = new CodeCell({
            contentFactory: new Cell.ContentFactory({
                editorFactory: factoryService.newInlineEditor
            }),
            model: new CodeCellModel(),
            rendermime,
            placeholder: false
        }).initializeState();
        // Trust the outputs and set the mimeType for the code
        this._cell.addClass('jp-blockly-codeCell');
        this._cell.readOnly = true;
        this._cell.model.trusted = true;
        this._cell.model.mimeType = this._manager.mimeType;
        // adding the style to the element as a quick fix
        // we should make it work with the css class
        this._cell.node.style.overflow = 'scroll';
        this._manager.changed.connect(this._onManagerChanged, this);
    }
    /*
     * The code cell.
     */
    get cell() {
        return this._cell;
    }
    /*
     * The current workspace.
     */
    get workspace() {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        return Blockly.serialization.workspaces.save(this._workspace);
    }
    /*
     * Set a new workspace.
     */
    set workspace(workspace) {
        const data = workspace === null ? { variables: [] } : workspace;
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        Blockly.serialization.workspaces.load(data, this._workspace);
    }
    /**
     * Dispose of the resources held by the widget.
     */
    dispose() {
        this._manager.changed.disconnect(this._resizeWorkspace, this);
        Signal.clearData(this);
        this._workspace.dispose();
        super.dispose();
    }
    /**
     * Init the blockly layout
     */
    init() {
        super.init();
        // Add the blockly container into the DOM
        this.addWidget(this._host);
        this.addWidget(this._cell);
    }
    /**
     * Create an iterator over the widgets in the layout.
     */
    iter() {
        return [][Symbol.iterator]();
    }
    /**
     * Remove a widget from the layout.
     *
     * @param widget - The `widget` to remove.
     */
    removeWidget(widget) {
        return;
    }
    /**
     * Return the extra coded (if it exists), composed of the individual
     * data from each block in the workspace, which are defined in the
     * toplevel_init property. (e.g. : imports needed for the block)
     *
     * Add extra code example:
     * Blockly.Blocks['block_name'].toplevel_init = `import numpy`
     */
    getBlocksToplevelInit() {
        // Initalize string which will return the extra code provided
        // by the blocks, in the toplevel_init property.
        let finalToplevelInit = '';
        // Get all the blocks in the workspace in order.
        const ordered = true;
        const used_blocks = this._workspace.getAllBlocks(ordered);
        // For each block in the workspace, check if theres is a toplevel_init,
        // if there is, add it to the final string.
        for (const block in used_blocks) {
            const current_block = used_blocks[block].type;
            if (Blockly.Blocks[current_block].toplevel_init) {
                // console.log(Blockly.Blocks[current_block].toplevel_init);
                // Attach it to the final string
                const string = Blockly.Blocks[current_block].toplevel_init;
                finalToplevelInit = finalToplevelInit + string;
            }
        }
        // console.log(finalToplevelInit);
        return finalToplevelInit;
    }
    /*
     * Generates and runs the code from the current workspace.
     */
    run() {
        // Get extra code from the blocks in the workspace.
        const extra_init = this.getBlocksToplevelInit();
        // Serializing our workspace into the chosen language generator.
        const code = extra_init + this._manager.generator.workspaceToCode(this._workspace);
        //const code = "import ipywidgets as widgets\nwidgets.IntSlider()";
        this._cell.model.sharedModel.setSource(code);
        // Execute the code using the kernel, by using a static method from the
        // same class to make an execution request.
        if (this._sessionContext.hasNoKernel) {
            // Check whether there is a kernel
            showErrorMessage('Select a valid kernel', `There is not a valid kernel selected, select one from the dropdown menu in the toolbar.
        If there isn't a valid kernel please install 'xeus-python' from Pypi.org or using mamba.
        `);
        }
        else {
            CodeCell.execute(this._cell, this._sessionContext)
                .then(() => this._resizeWorkspace())
                .catch(e => console.error(e));
        }
    }
    /**
     * Handle `update-request` messages sent to the widget.
     */
    onUpdateRequest(msg) {
        super.onUpdateRequest(msg);
        this._resizeWorkspace();
    }
    /**
     * Handle `resize-request` messages sent to the widget.
     */
    onResize(msg) {
        super.onResize(msg);
        this._resizeWorkspace();
    }
    /**
     * Handle `fit-request` messages sent to the widget.
     */
    onFitRequest(msg) {
        super.onFitRequest(msg);
        this._resizeWorkspace();
    }
    /**
     * Handle `after-attach` messages sent to the widget.
     */
    onAfterAttach(msg) {
        super.onAfterAttach(msg);
        //inject Blockly with appropiate JupyterLab theme.
        this._workspace = Blockly.inject(this._host.node, {
            toolbox: this._manager.toolbox,
            theme: THEME
        });
        this._workspace.addChangeListener(() => {
            // Get extra code from the blocks in the workspace.
            const extra_init = this.getBlocksToplevelInit();
            // Serializing our workspace into the chosen language generator.
            const code = extra_init + this._manager.generator.workspaceToCode(this._workspace);
            this._cell.model.sharedModel.setSource(code);
        });
    }
    _resizeWorkspace() {
        //Resize logic.
        Blockly.svgResize(this._workspace);
    }
    _onManagerChanged(sender, change) {
        if (change === 'kernel') {
            // Get extra code from the blocks in the workspace.
            const extra_init = this.getBlocksToplevelInit();
            // Serializing our workspace into the chosen language generator.
            const code = extra_init + this._manager.generator.workspaceToCode(this._workspace);
            this._cell.model.sharedModel.setSource(code);
            this._cell.model.mimeType = this._manager.mimeType;
        }
        if (change === 'toolbox') {
            this._workspace.updateToolbox(this._manager.toolbox);
        }
    }
}
//# sourceMappingURL=layout.js.map