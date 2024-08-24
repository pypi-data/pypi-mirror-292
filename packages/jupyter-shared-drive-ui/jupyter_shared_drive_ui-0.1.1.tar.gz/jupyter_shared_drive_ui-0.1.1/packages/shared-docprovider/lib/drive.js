// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.
import { PromiseDelegate } from '@lumino/coreutils';
import { WebrtcProvider as YWebrtcProvider } from 'y-webrtc';
import * as Y from 'yjs';
import { Signal } from '@lumino/signaling';
import { PageConfig, URLExt } from '@jupyterlab/coreutils';
//import { ServerConnection } from './serverconnection';
import { ServerConnection } from '@jupyterlab/services';
import { WebrtcProvider } from './provider';
const signalingServers = JSON.parse(PageConfig.getOption('signalingServers'));
const MODEL = {
    name: '',
    path: '',
    type: '',
    writable: true,
    created: '',
    last_modified: '',
    mimetype: '',
    content: '',
    format: null
};
/**
 * A collaborative implementation for an `IDrive`, talking to other peers using WebRTC.
 */
export class SharedDrive {
    /**
     * Construct a new drive object.
     *
     * @param user - The user manager to add the identity to the awareness of documents.
     */
    constructor(user, defaultFileBrowser, translator, globalAwareness, name) {
        this._onSync = (synced) => {
            var _a;
            if (synced.synced) {
                this._ready.resolve();
                (_a = this._fileSystemProvider) === null || _a === void 0 ? void 0 : _a.off('synced', this._onSync);
            }
        };
        this._onCreate = (options, sharedModel) => {
            if (typeof options.format !== 'string') {
                return;
            }
            const file = this._fileSystemContent.get(options.path);
            if (file === undefined) {
                return;
            }
            const key = `${options.format}:${options.contentType}:${options.path}`;
            const provider = new WebrtcProvider({
                url: '',
                path: options.path,
                format: options.format,
                contentType: options.contentType,
                model: sharedModel,
                user: this._user,
                translator: this._trans,
                signalingServers: this._signalingServers
            });
            this._fileProviders.set(key, provider);
            sharedModel.disposed.connect(() => {
                const provider = this._fileProviders.get(key);
                if (provider) {
                    provider.dispose();
                    this._fileProviders.delete(key);
                }
            });
        };
        this._fileChanged = new Signal(this);
        this._isDisposed = false;
        this._ready = new PromiseDelegate();
        this._signalingServers = [];
        this._user = user;
        //this._defaultFileBrowser = defaultFileBrowser;
        this._trans = translator;
        this._globalAwareness = globalAwareness;
        //this._username = this._globalAwareness?.getLocalState()?.user.identity.name;
        //this._username = this._globalAwareness?.getLocalState()?.username;
        this._fileProviders = new Map();
        this.sharedModelFactory = new SharedModelFactory(this._onCreate);
        this.serverSettings = ServerConnection.makeSettings();
        signalingServers.forEach((url) => {
            if (url.startsWith('ws://') || url.startsWith('wss://')) {
                // It's an absolute URL, keep it as-is.
                this._signalingServers.push(url);
            }
            else {
                // It's a Jupyter server relative URL, build the absolute URL.
                this._signalingServers.push(URLExt.join(this.serverSettings.wsUrl, url));
            }
        });
        this.name = name;
        this._fileSystemYdoc = new Y.Doc();
        this._fileSystemContent = this._fileSystemYdoc.getMap('content');
        this._fileSystemProvider = new YWebrtcProvider('fileSystem', this._fileSystemYdoc, {
            signaling: this._signalingServers,
            awareness: this._globalAwareness || undefined
        });
        this._fileSystemProvider.on('synced', this._onSync);
    }
    getDownloadUrl(path) {
        return new Promise(resolve => {
            resolve('');
        });
    }
    delete(path) {
        return new Promise(resolve => {
            resolve();
        });
    }
    restoreCheckpoint(path, checkpointID) {
        return new Promise(resolve => {
            resolve();
        });
    }
    deleteCheckpoint(path, checkpointID) {
        return new Promise(resolve => {
            resolve();
        });
    }
    //async importFile(path: string) {
    //  const model = await this._defaultFileBrowser.model.manager.services.contents.get(path, {content: true});
    //  const ymap = new Y.Map();
    //  const ytext = new Y.Text();
    //  this._fileSystemContent.set(model.name, ymap);
    //  ymap.set('init', new Y.Map());
    //  ymap.set('content', ytext);
    //  ytext.insert(0, model.content);
    //}
    async newUntitled(options = {}) {
        if (options.type === 'directory') {
            throw new Error('Cannot create directory');
        }
        let ext;
        if (options.type === 'notebook') {
            ext = 'ipynb';
        }
        else {
            ext = 'txt';
        }
        let idx = 0;
        let newName = '';
        const fileSystemContent = this._fileSystemContent.toJSON();
        while (newName === '') {
            const _newName = `untitled${idx}.${ext}`;
            if (_newName in fileSystemContent) {
                idx += 1;
            }
            else {
                newName = _newName;
            }
        }
        const model = {
            name: newName,
            path: newName,
            type: 'file',
            writable: true,
            created: '',
            last_modified: '',
            mimetype: '',
            content: null,
            format: null
        };
        const ymap = new Y.Map();
        this._fileSystemContent.set(newName, ymap);
        this._fileChanged.emit({
            type: 'new',
            oldValue: null,
            newValue: model
        });
        return model;
    }
    async rename(path, newPath) {
        const fileSystemContent = this._fileSystemContent.toJSON();
        if (path in fileSystemContent) {
            this._fileSystemContent.delete(path);
        }
        if (!(newPath in fileSystemContent)) {
            const ymap = new Y.Map();
            this._fileSystemContent.set(newPath, ymap);
        }
        const model = {
            name: newPath,
            path: newPath,
            type: 'file',
            writable: true,
            created: '',
            last_modified: '',
            mimetype: '',
            content: null,
            format: null
        };
        return model;
    }
    copy(path, toDir) {
        return new Promise(resolve => {
            resolve(MODEL);
        });
    }
    createCheckpoint(path) {
        const model = {
            id: '',
            last_modified: ''
        };
        return new Promise(resolve => {
            resolve(model);
        });
    }
    listCheckpoints(path) {
        return new Promise(resolve => {
            resolve([]);
        });
    }
    /**
     * A signal emitted when a file operation takes place.
     */
    get fileChanged() {
        return this._fileChanged;
    }
    /**
     * Test whether the manager has been disposed.
     */
    get isDisposed() {
        return this._isDisposed;
    }
    /**
     * Dispose of the resources held by the manager.
     */
    dispose() {
        if (this.isDisposed) {
            return;
        }
        this._fileProviders.forEach(p => p.dispose());
        this._fileProviders.clear();
        this._isDisposed = true;
        Signal.clearData(this);
    }
    /**
     * Get a file or directory.
     *
     * @param localPath: The path to the file.
     *
     * @param options: The options used to fetch the file.
     *
     * @returns A promise which resolves with the file content.
     *
     * Uses the [Jupyter Notebook API](http://petstore.swagger.io/?url=https://raw.githubusercontent.com/jupyter/notebook/master/notebook/services/api/api.yaml#!/contents) and validates the response model.
     */
    async get(localPath, options) {
        let model;
        await this._ready;
        if (options && options.format && options.type) {
            // it's a file
            const key = `${options.format}:${options.type}:${localPath}`;
            const provider = this._fileProviders.get(key);
            if (provider) {
                //await provider.ready;
                model = {
                    name: localPath,
                    path: localPath,
                    type: 'file',
                    writable: true,
                    created: '',
                    last_modified: '',
                    mimetype: '',
                    content: null,
                    format: null
                };
                return new Promise(resolve => {
                    resolve(model);
                });
            }
        }
        // it's a directory
        const content = [];
        if (localPath === '') {
            // root directory
            this._fileSystemContent.forEach((value, key) => {
                content.push({
                    name: key,
                    path: key,
                    type: 'file',
                    writable: true,
                    created: '',
                    last_modified: '',
                    mimetype: '',
                    content: null,
                    format: null
                });
            });
            model = {
                name: '',
                path: '',
                type: 'directory',
                writable: false,
                created: '',
                last_modified: '',
                mimetype: '',
                content,
                format: null
            };
        }
        else {
            model = {
                name: localPath,
                path: localPath,
                type: 'file',
                writable: true,
                created: '',
                last_modified: '',
                mimetype: '',
                content: null,
                format: null
            };
        }
        return new Promise(resolve => {
            resolve(model);
        });
    }
    /**
     * Save a file.
     *
     * @param localPath - The desired file path.
     *
     * @param options - Optional overrides to the model.
     *
     * @returns A promise which resolves with the file content model when the
     *   file is saved.
     */
    async save(localPath, options = {}) {
        // Check that there is a provider - it won't e.g. if the document model is not collaborative.
        if (options.format && options.type) {
            const key = `${options.format}:${options.type}:${localPath}`;
            const provider = this._fileProviders.get(key);
            if (provider) {
                // Save is done from the backend
                const fetchOptions = {
                    type: options.type,
                    format: options.format,
                    content: false
                };
                return this.get(localPath, fetchOptions);
            }
        }
        return new Promise(resolve => {
            resolve(MODEL);
        });
        //return super.save(localPath, options);
    }
}
/**
 * Yjs sharedModel factory for real-time collaboration.
 */
class SharedModelFactory {
    /**
     * Shared model factory constructor
     *
     * @param _onCreate Callback on new document model creation
     */
    constructor(_onCreate) {
        this._onCreate = _onCreate;
        this._documentFactories = new Map();
    }
    /**
     * Register a SharedDocumentFactory.
     *
     * @param type Document type
     * @param factory Document factory
     */
    registerDocumentFactory(type, factory) {
        if (this._documentFactories.has(type)) {
            throw new Error(`The content type ${type} already exists`);
        }
        this._documentFactories.set(type, factory);
    }
    /**
     * Create a new `ISharedDocument` instance.
     *
     * It should return `undefined` if the factory is not able to create a `ISharedDocument`.
     */
    createNew(options) {
        if (typeof options.format !== 'string') {
            console.warn(`Only defined format are supported; got ${options.format}.`);
            return;
        }
        if (this._documentFactories.has(options.contentType)) {
            const factory = this._documentFactories.get(options.contentType);
            const sharedModel = factory(options);
            this._onCreate(options, sharedModel);
            return sharedModel;
        }
        return;
    }
}
