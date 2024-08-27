# Other extensions

The JupyterLab-Blockly extension is ready to be used as a base for other projects: you can register new Blocks, Toolboxes and Generators. It is a great tool for fast prototyping.

## Creating a new JupyterLab extension
You can easily create a new JupyterLab extension by using the official `copier` template, documented [here](https://github.com/jupyterlab/extension-template).

After installing the needed plugins (mentioned in the above link) and creating an extension directory, you can run the following command:
```
copier copy --trust https://github.com/jupyterlab/extension-template .
```
which will ask you to fill some basic information about your project. Once completed, the directory will be populated with several files, all forming the base of your project. You will mostly work in the `index.ts` file, located in the `src` folder.

An example of creating a simple JupyterLab extension, which also contains the instructions of how to fill the information asked by the `copier` template, can be found [here](https://github.com/jupyterlab/extension-examples/tree/master/hello-world).


## Importing JupyterLab-Blockly
Firstly you need to install and add `jupyterlab-blockly` as a dependency for your extension:
```
jlpm add jupyterlab-blockly
```

Once it is part of your project, all you need to do is import `IBlocklyRegistry`, as it follows:
```typescript
// src/index.ts

import { IBlocklyRegistry } from 'jupyterlab-blockly';
```

The `BlocklyRegistry` is the class that the JupyterLab-Blockly extension exposes to other plugins. This registry allows other plugins to register new Toolboxes, Blocks and Generators that users can use in the Blockly editor.

### Registering new Blocks
The `IBlocklyRegistry` offers a function `registerBlocks`, which allows you to include new Blocks in your project. Blockly offers a [tool](https://blockly-demo.appspot.com/static/demos/blockfactory/index.html) which helps you easily create new Blocks and get their JSON definition and generator code in all supported programming languages.

**NOTE** : Once you create a new block, it won't appear into your Blockly editor, unless you add it to a Toolbox.

```typescript
 /**
   * Register new blocks.
   *
   * @argument blocks Blocks to register.
   */
  registerBlocks(blocks: BlockDefinition[]): void {
    Blockly.defineBlocksWithJsonArray(blocks);
  }
```

### Registering a new Toolbox
Using the `registerToolbox` function, provided by `IBlocklyRegistry`, you can register a new toolbox. Once registered, the toolbox will appear automatically in your Blockly editor. You can find more information about switching to another toolbox [here](https://jupyterlab-blockly.readthedocs.io/en/latest/toolbox.html).

```typescript
/**
   * Register a toolbox for the editor.
   *
   * @argument name Name of the toolbox.
   *
   * @argument value Toolbox to register.
   */
  registerToolbox(name: string, value: ToolboxDefinition): void {
    this._toolboxes.set(name, value);
  }
```

### Registering a new Generator
Lastly, `IBlocklyRegistry` offers the function `registerGenerator` which lets you register a new Generator. You can read more about switching kernels [here](https://jupyterlab-blockly.readthedocs.io/en/latest/kernels.html).

```typescript

  /**
   * Register new generators.
   *
   * @argument name Name of the generator.
   *
   * @argument generator Generator to register.
   *
   * #### Notes
   * When registering a generator, the name should correspond to the language
   * used by a kernel.
   *
   * If you register a generator for an existing language this will be overwritten.
   */
  registerGenerator(name: string, generator: Blockly.Generator): void {
    this._generators.set(name, generator);
  }
```


## Example - JupyterLab-Niryo-One
The [JupyterLab-Niryo-One](https://github.com/QuantStack/jupyterlab-niryo-one/) extension was built on top of JupyterLab-Blockly and poses as the perfect example. The [Github repository](https://github.com/QuantStack/jupyterlab-niryo-one/) gives access to its entire codebase.

The following code snippet showcases how to register a new toolbox, `BlocklyNiryo.Toolbox`, as `niryo`.
```typescript
// src/index.ts : 10-23

/**
 * Initialization data for the jupyterlab-niryo-one extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-niryo-one:plugin',
  autoStart: true,
  requires: [IBlocklyRegistry],
  activate: (app: JupyterFrontEnd, blockly: IBlocklyRegistry) => {
    console.log('JupyterLab extension jupyterlab-niryo-one is activated!');

    //Registering the new toolbox containing all Niryo One blocks.
    blockly.registerToolbox('niryo', BlocklyNiryo.Toolbox);
  }
};
```

**NOTE** : `BlocklyNiryo` is defined in `niryo-one-python-generators.ts`.


## Additional configurations

You will need to request the `jupyterlab-blockly` package as a dependency for your extension, in order to ensure it is installed and available to provide the token `IBlocklyRegistry`. To do this, you need to add the following line to your `pyproject.toml` file.

```
// pyproject.toml : 26

dependencies = [
    "jupyterlab-blockly>=0.3.2,<0.4",
    ... // add any additional dependencies needed for your extension
]
```

Additionally, you will need to add the webpack configuration for loading the `Blockly` source maps. You can do this, by creating the following `webpack.config.js` file inside your root directory:

```js
// @ts-check

module.exports = /** @type { import('webpack').Configuration } */ ({
  devtool: 'source-map',
  module: {
    rules: [
      // Load Blockly source maps.
      {
        test: /(blockly\/.*\.js)$/,
        use: [require.resolve('source-map-loader')],
        enforce: 'pre'
      }
    ].filter(Boolean)
  },
  // https://github.com/google/blockly-samples/blob/9974e85becaa8ad17e35b588b95391c85865dafd/plugins/dev-scripts/config/webpack.config.js#L118-L120
  ignoreWarnings: [/Failed to parse source map/]
});
```

and by connecting the `webpack` config to your `jupyterlab` instance, which entails adding the following line inside your `package.json`: 

```json
"jupyterlab": {
    ...
    "webpackConfig": "./webpack.config.js"
  }
```