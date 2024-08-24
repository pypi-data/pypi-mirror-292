import { DocumentChange, YDocument } from '@jupyter/ydoc';
import { Contents } from '@jupyterlab/services';
import { Token } from '@lumino/coreutils';
/**
 * The collaborative drive.
 */
export declare const ISharedDrive: Token<ISharedDrive>;
/**
 * A document factory for registering shared models
 */
export type SharedDocumentFactory = (options: Contents.ISharedFactoryOptions) => YDocument<DocumentChange>;
/**
 * A Collaborative implementation for an `IDrive`, talking to the
 * server using the Jupyter REST API and a WebSocket connection.
 */
export interface ISharedDrive extends Contents.IDrive {
    /**
     * SharedModel factory for the SharedDrive.
     */
    readonly sharedModelFactory: ISharedModelFactory;
}
/**
 * Yjs sharedModel factory for real-time collaboration.
 */
export interface ISharedModelFactory extends Contents.ISharedFactory {
    /**
     * Register a SharedDocumentFactory.
     *
     * @param type Document type
     * @param factory Document factory
     */
    registerDocumentFactory(type: Contents.ContentType, factory: SharedDocumentFactory): void;
}
