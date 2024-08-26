# Convection Plugin - Secrets

- [Convection Plugin - Secrets](#convection-plugin---secrets)
  - [Utilizing](#utilizing)
  - [Building](#building)
    - [Metadata](#metadata)
    - [Functions / Methods](#functions--methods)
    - [Encryption / Decryption](#encryption--decryption)

## Utilizing

Plugins can be installed via pip, once installed, the server must be restarted completely (stop + start), and will become available in the Store Types listing.

## Building

Plugins must be derived from `ConvectionPlugin_Secret` class.

### Metadata

Convection Plugins use a section of configuration (or definition in code) to define data such as Version, Name, Type, Description, Date Plugin was updated, etc. This data is used for the plugin repository (future) and for version compatibility checks, etc.

This data must be in the following structure:

```json
{
    "version": "1.0.0",
    "author": "$AUTHOR_NAME <$AUTHOR_EMAIL>",
    "updated": $DATE_MODIFIED,
    "compatibility": "$VERSION_COMPAT_STRING",
    "plugin": {
        "name": "$PLUGIN_NAME",
        "type": "$PLUGIN_TYPE",
        "description": "$PLUGIN_DESCRIPTION"
    }
}
```

 - `plugin.type` should be, in this case `Secret`.
 - `plugin.name`Name would be the String name of the secrets type, for example if the file name is `generic` then the `plugin.name` would be `Generic`.
 - `version` should be incremented any time this plugin changes. Be sure to follow `Major.Minor.Patch`. Where `Major` are breaking changes, `Minor` are Feature additions, or non breaking changes, and `Patch` are bugfixes
 - `compatibility` is a version search string that can be used to verify that the plugin version that was last used to write data is compatible with the active plugin version. Search strings are in the form of `<comparator>:<version>,...` such as: `>=:1.0,<:2.0`, which would match any version greater than or equal to 1.0 but less than 2.0.

### Functions / Methods

The Generic Secrets Plugin can be used as an example of a very basic key/value store, and covers descriptions and examples of what these functions should and must do.

Protected functions that must be defined for each Secrets Store

 - `_close`: Close / Clear Data, signaling completion of read or write operations
 - `_read`: Read Data from Store into Memory
 - `_write`: Write Data from Memory into Store

Public functions that must be defined for each Store

 - `initialize`: New Store creation, Write Empty Data / Empty Structure
 - `rotate`: Encryption Key rotation
 - `create`: Create / Add new piece of data into Store
 - `destroy`: Destroy / Remove data from Store
 - `get`: Get Unencrypted data from Store
 - `modify`: Modify / Change existing data that is already in Store
 - `list`: Get List of registered Secrets
 - `configure`: Secrets Store Configuration Read/Write
 - `info`: Information about Secrets Store (Number of secrets, reads/writes, metadata, etc)
 - `marked_for_delete`: Secrets Store Deletion steps

### Encryption / Decryption

The Fernet object is stored in `_encryptor` in the Plugin Object variables. This is used to encrypt/decrypt the stored data.
