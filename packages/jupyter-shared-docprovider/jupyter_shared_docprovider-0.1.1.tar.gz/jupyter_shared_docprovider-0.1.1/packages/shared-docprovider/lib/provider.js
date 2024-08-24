/* -----------------------------------------------------------------------------
| Copyright (c) Jupyter Development Team.
| Distributed under the terms of the Modified BSD License.
|----------------------------------------------------------------------------*/
import { PromiseDelegate } from '@lumino/coreutils';
import { Signal } from '@lumino/signaling';
import { WebrtcProvider as YWebrtcProvider } from 'y-webrtc';
/**
 * A class to provide Yjs synchronization over WebSocket.
 *
 * We specify custom messages that the server can interpret. For reference please look in yjs_ws_server.
 *
 */
export class WebrtcProvider {
    /**
     * Construct a new WebSocketProvider
     *
     * @param options The instantiation options for a WebSocketProvider
     */
    constructor(options) {
        //private _onConnectionClosed = (event: any): void => {
        //  if (event.code === 1003) {
        //    console.error('Document provider closed:', event.reason);
        //    showErrorMessage(this._trans.__('Document session error'), event.reason, [
        //      Dialog.okButton()
        //    ]);
        //    // Dispose shared model immediately. Better break the document model,
        //    // than overriding data on disk.
        //    this._sharedModel.dispose();
        //  }
        //};
        this._onSync = (synced) => {
            if (synced.synced) {
                this._ready.resolve();
                //this._yWebrtcProvider?.off('status', this._onSync);
            }
        };
        this._ready = new PromiseDelegate();
        this._isDisposed = false;
        this._path = options.path;
        this._contentType = options.contentType;
        this._format = options.format;
        this._sharedModel = options.model;
        this._awareness = options.model.awareness;
        this._yWebrtcProvider = null;
        //this._trans = options.translator;
        this._signalingServers = options.signalingServers;
        const user = options.user;
        user.ready
            .then(() => {
            this._onUserChanged(user);
        })
            .catch(e => console.error(e));
        user.userChanged.connect(this._onUserChanged, this);
        this._connect().catch(e => console.warn(e));
    }
    /**
     * Test whether the object has been disposed.
     */
    get isDisposed() {
        return this._isDisposed;
    }
    /**
     * A promise that resolves when the document provider is ready.
     */
    get ready() {
        return this._ready.promise;
    }
    /**
     * Dispose of the resources held by the object.
     */
    dispose() {
        var _a;
        if (this.isDisposed) {
            return;
        }
        this._isDisposed = true;
        //this._yWebrtcProvider?.off('connection-close', this._onConnectionClosed);
        //this._yWebrtcProvider?.off('status', this._onSync);
        (_a = this._yWebrtcProvider) === null || _a === void 0 ? void 0 : _a.destroy();
        Signal.clearData(this);
    }
    async _connect() {
        this._yWebrtcProvider = new YWebrtcProvider(`${this._format}:${this._contentType}:${this._path}}`, this._sharedModel.ydoc, {
            signaling: this._signalingServers,
            awareness: this._awareness
        });
        this._yWebrtcProvider.on('synced', this._onSync);
        //this._yWebrtcProvider.on('connection-close', this._onConnectionClosed);
    }
    _onUserChanged(user) {
        this._awareness.setLocalStateField('user', user.identity);
    }
}
