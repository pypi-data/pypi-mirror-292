import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import { ISharedDrive } from '@jupyter/shared-docprovider';
/**
 * The shared drive provider.
 */
export declare const drive: JupyterFrontEndPlugin<ISharedDrive>;
/**
 * Plugin to register the shared model factory for the content type 'file'.
 */
export declare const yfile: JupyterFrontEndPlugin<void>;
/**
 * Plugin to register the shared model factory for the content type 'notebook'.
 */
export declare const ynotebook: JupyterFrontEndPlugin<void>;
/**
 * The shared file browser factory provider.
 */
export declare const sharedFileBrowser: JupyterFrontEndPlugin<void>;
