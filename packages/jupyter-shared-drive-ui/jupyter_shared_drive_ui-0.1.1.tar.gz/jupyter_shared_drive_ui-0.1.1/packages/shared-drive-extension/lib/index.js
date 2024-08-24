// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.
/**
 * @packageDocumentation
 * @module shared-drive-extension
 */
import { userMenuPlugin, menuBarPlugin, rtcGlobalAwarenessPlugin, userEditorCursors } from './collaboration';
/**
 * Export the plugins as default.
 */
const plugins = [
    userMenuPlugin,
    menuBarPlugin,
    rtcGlobalAwarenessPlugin,
    userEditorCursors
];
export default plugins;
