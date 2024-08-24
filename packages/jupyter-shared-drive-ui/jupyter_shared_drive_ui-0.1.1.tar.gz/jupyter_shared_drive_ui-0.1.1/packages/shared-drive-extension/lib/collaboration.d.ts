/**
 * @packageDocumentation
 * @module shared-drive-extension
 */
import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IAwareness } from '@jupyter/ydoc';
import { IUserMenu } from '@jupyter/shared-drive';
/**
 * Jupyter plugin providing the IUserMenu.
 */
export declare const userMenuPlugin: JupyterFrontEndPlugin<IUserMenu>;
/**
 * Jupyter plugin adding the IUserMenu to the menu bar if collaborative flag enabled.
 */
export declare const menuBarPlugin: JupyterFrontEndPlugin<void>;
/**
 * Jupyter plugin creating a global awareness for RTC.
 */
export declare const rtcGlobalAwarenessPlugin: JupyterFrontEndPlugin<IAwareness>;
export declare const userEditorCursors: JupyterFrontEndPlugin<void>;
