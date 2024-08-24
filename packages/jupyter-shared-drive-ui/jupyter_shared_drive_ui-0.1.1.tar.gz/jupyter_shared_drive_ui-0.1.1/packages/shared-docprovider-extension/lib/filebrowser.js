/*
 * Copyright (c) Jupyter Development Team.
 * Distributed under the terms of the Modified BSD License.
 */
import { listIcon, refreshIcon } from '@jupyterlab/ui-components';
//import { listIcon, fileIcon, refreshIcon } from '@jupyterlab/ui-components';
import { ILabShell, IRouter, JupyterFrontEnd } from '@jupyterlab/application';
import { ToolbarButton } from '@jupyterlab/apputils';
import { IDefaultFileBrowser, IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ITranslator } from '@jupyterlab/translation';
import { YFile, YNotebook } from '@jupyter/ydoc';
import { IGlobalAwareness } from '@jupyter/shared-drive';
import { ISharedDrive, SharedDrive } from '@jupyter/shared-docprovider';
/**
 * The shared drive provider.
 */
export const drive = {
    id: '@jupyter/docprovider-extension:drive',
    description: 'The default collaborative drive provider',
    provides: ISharedDrive,
    requires: [IDefaultFileBrowser, ITranslator],
    optional: [IGlobalAwareness],
    activate: (app, defaultFileBrowser, translator, globalAwareness) => {
        const trans = translator.load('jupyter-shared-drive');
        const drive = new SharedDrive(app.serviceManager.user, defaultFileBrowser, trans, globalAwareness, 'Shared');
        return drive;
    }
};
/**
 * Plugin to register the shared model factory for the content type 'file'.
 */
export const yfile = {
    id: '@jupyter/docprovider-extension:yfile',
    description: "Plugin to register the shared model factory for the content type 'file'",
    autoStart: true,
    requires: [ISharedDrive],
    optional: [],
    activate: (app, drive) => {
        const yFileFactory = () => {
            return new YFile();
        };
        drive.sharedModelFactory.registerDocumentFactory('file', yFileFactory);
    }
};
/**
 * Plugin to register the shared model factory for the content type 'notebook'.
 */
export const ynotebook = {
    id: '@jupyter/docprovider-extension:ynotebook',
    description: "Plugin to register the shared model factory for the content type 'notebook'",
    autoStart: true,
    requires: [ISharedDrive],
    optional: [ISettingRegistry],
    activate: (app, drive, settingRegistry) => {
        let disableDocumentWideUndoRedo = true;
        // Fetch settings if possible.
        if (settingRegistry) {
            settingRegistry
                .load('@jupyterlab/notebook-extension:tracker')
                .then(settings => {
                const updateSettings = (settings) => {
                    var _a;
                    const enableDocWideUndo = settings === null || settings === void 0 ? void 0 : settings.get('experimentalEnableDocumentWideUndoRedo').composite;
                    disableDocumentWideUndoRedo = (_a = !enableDocWideUndo) !== null && _a !== void 0 ? _a : true;
                };
                updateSettings(settings);
                settings.changed.connect((settings) => updateSettings(settings));
            });
        }
        const yNotebookFactory = () => {
            return new YNotebook({
                disableDocumentWideUndoRedo
            });
        };
        drive.sharedModelFactory.registerDocumentFactory('notebook', yNotebookFactory);
    }
};
/**
 * The shared file browser factory provider.
 */
export const sharedFileBrowser = {
    id: 'jupyterlab-shared-contents:sharedFileBrowser',
    description: 'The shared file browser factory provider',
    autoStart: true,
    requires: [ISharedDrive, IFileBrowserFactory],
    optional: [
        IRouter,
        JupyterFrontEnd.ITreeResolver,
        ILabShell,
        ISettingRegistry,
        ITranslator
    ],
    activate: async (app, drive, fileBrowserFactory, router, tree, labShell, translator) => {
        const { createFileBrowser } = fileBrowserFactory;
        //const trans = (translator ?? nullTranslator).load('jupyterlab-shared-contents');
        app.serviceManager.contents.addDrive(drive);
        const widget = createFileBrowser('jp-shared-contents-browser', {
            driveName: drive.name,
            // We don't want to restore old state, we don't have a drive handle ready
            restore: false
        });
        //widget.title.caption = trans.__('Shared Contents');
        widget.title.caption = 'Shared Contents';
        widget.title.icon = listIcon;
        //const importButton = new ToolbarButton({
        //  icon: fileIcon,
        //  onClick: async () => {
        //    let path = prompt('Please enter the path of the file to import:');
        //    if (path !== null) {
        //      await drive.importFile(path);
        //    }
        //  },
        //  tooltip: 'Import File'
        //});
        const refreshButton = new ToolbarButton({
            icon: refreshIcon,
            onClick: async () => {
                widget.model.refresh();
            },
            tooltip: 'Refresh File Browser'
        });
        widget.toolbar.insertItem(0, 'refresh', refreshButton);
        //widget.toolbar.insertItem(1, 'import', importButton);
        app.shell.add(widget, 'left');
    }
};
