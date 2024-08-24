// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.
/**
 * @packageDocumentation
 * @module shared-drive-extension
 */
import { drive, yfile, ynotebook, sharedFileBrowser } from './filebrowser';
/**
 * Export the plugins as default.
 */
const plugins = [
    drive,
    yfile,
    ynotebook,
    sharedFileBrowser
];
export default plugins;
