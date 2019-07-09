FORMAT: 1A
HOST: http://localhost:5000/

# MusicMeta API

This API is a simple music metadata service for artists, albums (and other releases) and tracks. The API serves JSON data extended by the [Mason hypermedia format](https://github.com/JornWildt/Mason). Custom link relations and resource profiles have been included in this API document - they are not resources.

# Group Link Relations

This section described custom link relations defined in this API. These are not resources. The API also uses 
[IANA link relations](http://www.iana.org/assignments/link-relations/link-relations.xhtml) where applicable. Custom link relations are CURIEs that use the mumeta prefix. 

## add-album

This is a control that is used to add an album to the associated collection resource. The control includes a JSON schema and must be accessed with POST. 

## add-track

This is a control that is used to add a track to an album resource. The control includes a JSON schema and must be accessed with POST.

## albums-all

Leads to the root level albums collection which is a list of all albums known to the API regardless of artist. This collection can be sorted using query parameters as described in the resource documentation.

## albums-by

Leads to a collection resoruce that includes all albums by the associated artist.

## albums-va

Leads to a collection resource that includes all collaborative albums (various artists, VA).

## artists-all

Leads to the root level artists collection which is a list of all artists known to the API. 

## delete

Deletes the associated resource. Must be accessed with DELETE

# Group Profiles

This section includes resource profiles which provide semantic descriptions for the attributes of each resource, as well as the list of controls (by link relation) available from that resource.

## Album Profile

Profile definition for all album related resources.

### Link Relations

This section lists all possible link relations associated with albums; not all of them are necessarily present on each resource type. The following link relations from the mumeta namespace are used:

 * [add-album](reference/link-relations/add-album)
 * [add-track](reference/link-relations/add-track)
 * [albums-all](reference/link-relations/albums-all)
 * [albums-va](reference/link-relations/albums-va)
 * [artists-all](reference/link-relations/artists-all)
 * [delete](reference/link-relations/delete)
 
The following [IANA RFC5988](http://www.iana.org/assignments/link-relations/link-relations.xhtml) link relations are also used:

 * author
 * collection
 * edit
 * profile
 * self
 
### Semantic Descriptors

#### Data Type Album

 * `title`: The albums title as it is written on the release, including capitalization and punctuation. Titles are unique per artist, and are used to address album resources. Mandatory.
 * `release`: Album's release date in [ISO 8601 format](https://www.iso.org/iso-8601-date-and-time-format.html) (YYYY-MM-DD). Use 01 for month or day if not known. Mandatory.
 * `artist`: The album's artist's name (null for VA albums), including capitalization and pucntuation.
 * `discs`: Number of discs the album contains. Default is 1.
 * `genre`: The albums musical genre as a string. Optional.

## Error Profile

Profile definition for all errors returned by the API. See [Mason error control](https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md#property-name-error) for more information about errors.

+ Attributes

    + resource_url (string, required) - URI of the resource the error was generated from. 
 
## Track Profile

Profile definition for all track related resources.

### Link Relations

This section lists all possible link relations associated with tracks; not all of them are necessarily present on each resource type. The following link relations from the mumeta namespace are used:

 * [albums-by](reference/link-relations/albums-by)
 * [delete](reference/link-relations/delete)
 
The following [IANA RFC5988](http://www.iana.org/assignments/link-relations/link-relations.xhtml) link relations are also used:

 * author
 * edit
 * profile
 * self
 * up

### Semantic Descriptors

#### Data Type Track

 * `title`: The track's title as it is written on the release, including capitalization and punctuation. Not unique. Mandatory.
 * `artist`: The track artist's name which is either the album artist, or the track's artist on VA albums.
 * `length`: Track length as a time in [ISO 8601 format](https://www.iso.org/iso-8601-date-and-time-format.html) (hh:mm:ss). Mandatory.
 * `disc_number`: Number of the disc of the album this track is on. Default is 1. Unique together with track number per album.
 * `track_number`: Number of the track on the disc it's on. Mandatory. Unique together with disc number per album. 
 
# Group Entry

This group contains the entry point of the API

## Entry Point [/api/]

### Get entry point [GET]

Get the API entry point

+ Request

    + Headers
    
            Accept: application/vnd.mason+json
            
+ Response 200 (application/vnd.mason+json)

    + Body
    
            {
                "@namespaces": {
                    "mumeta": {
                        "name": "/musicmeta/link-relations#"
                    }
                },
                "@controls": {
                    "mumeta:albums-all": {
                        "href": "/api/albums/"
                    },
                    "mumeta:artists-all": {
                        "href": "/api/artists/"
                    }
                }
            }

 
# Group Albums

All of these resources use the [Album Profile](reference/profiles/album-profile). In error scenarios [Error Profile](reference/profiles/error-profile) is used.

## Album Collection [/api/albums/?sortby={field}]

A list of all albums known to the API. This collection can be sorted using the sortby query parameter. For each album only artist name and title is included, more information can be found by following the `self` relation of each album. Albums cannot be directly added to this collection, it only supports GET.

+ Parameters

    + field (string, optional) - Field to use for sorting
    
        + Default: `title`
        + Members
        
            + `artist`
            + `title`
            + `genre`
            + `release`

### List all albums [GET]

Get a list of all albums known to the API.

+ Relation: albums-all
+ Request

    + Headers
    
            Accept: application/vnd.mason+json

+ Response 200 (application/vnd.mason+json)
    
    + Body

            {
                "@namespaces": {
                    "mumeta": {
                        "name": "/musicmeta/link-relations#"
                    }
                },
                "@controls": {
                    "self": {
                        "href": "/api/albums/"
                    },
                    "mumeta:artists-all": {
                        "href": "/api/artists/",
                        "title": "All artists"
                    },
                    "mumeta:albums-va": {
                        "href": "/api/artists/VA/albums/",
                        "title": "All VA albums"
                    }
                },
                "items": [
                    {
                        "title": "Hello World",
                        "artist": "Scandal",
                        "@controls": {
                            "self": {
                                "href": "/api/artists/scandal/Hello World/"
                            }, 
                            "profile": {
                                "href": "/profiles/album/"
                            }
                        },
                    }, 
                    {
                        "title": "Thorns vs Emperor",
                        "artist": "VA",
                        "@controls": {
                            "self": {
                                "href": "/api/artists/VA/Thorns vs Emperor/"
                            },
                            "profile": {
                                "href": "/profiles/album/"
                            }
                        }
                    }
                ]
            }
        
## Albums by Artist [/api/artists/{artist}/albums/]

This is an album collection by given artist using the artist's unique name. For each album only artist and title is included, more information can be found by following the `self` relation of each album. Albums released by this artist can be added to this collection.

+ Parameters

    + artist: scandal (string) - artist's unique name (unique_name)

### List albums by artist [GET]

Get a list of albums by an artist.

+ Relation: albums-by
+ Request

    + Headers
    
            Accept: application/vnd.mason+json
    
+ Response 200 (application/vnd.mason+json)

    + Body
    
            {
                "@namespaces": {
                    "mumeta": {
                        "name": "/musicmeta/link-relations#"
                    }
                }, 
                "@controls": {
                    "self": {
                        "href": "/api/artists/scandal/albums/"
                    },
                    "mumeta:artists-all": {
                        "href": "/api/artists/",
                        "title": "All artists"
                    },                    
                    "mumeta:albums-all": {
                        "href": "/api/albums/?{sortby}",
                        "title": "All albums",
                        "isHrefTemplate": true,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "sortby": {
                                    "description": "Field to use for sorting",
                                    "type": "string",
                                    "default": "title",
                                    "enum": ["artist", "title", "genre", "release"]
                                }
                            },
                            "required": []
                        }
                    },                    
                    "author": {
                        "href": "/api/artists/scandal/"
                    },
                    "mumeta:add-album": {
                        "href": "/api/artists/scandal/albums/",
                        "title": "Add a new album for this artist",
                        "encoding": "json",
                        "method": "POST",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "description": "Album title",
                                    "type": "string"
                                },
                                "release": {
                                    "description": "Release date",
                                    "type": "string",
                                    "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]$"
                                },
                                "genre": {
                                    "description": "Album's genre(s)",
                                    "type": "string"
                                },
                                "discs": {
                                    "description": "Number of discs",
                                    "type": "integer",
                                    "default": 1
                                }
                            },
                            "required": ["title", "release"]
                        }
                    }
                },
                "items": [
                    {
                        "title": "Hello World",
                        "artist": "Scandal",
                        "@controls": {
                            "self": {
                                "href": "/api/artists/scandal/albums/Hello World/"
                            },
                            "profile": {
                                "href": "/profiles/album/"
                            }
                        }
                    }
                ]
            }

+ Response 404 (application/vnd.mason+json)

    The client is trying to retrieve list of albums for an artist that doesn't exist.

    + Body
    
            
            {
                "resource_url": "/api/artists/hemuli/albums/",
                "@error": {
                    "@message": "Artist not found",
                    "@messages": [null]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

### Add album for artist [POST]

Adds a new album for the artist. The album representation must be valid against the album schema.

+ Relation: add-album
+ Request (application/json)

    + Headers

            Accept: application/vnd.mason+json
        
    + Body
    
            {
                "title": "Best Scandal",
                "release": "2009-10-21",
                "genre": "Pop Rock",
                "discs": 1
            }

+ Response 201

    + Headers
    
            Location: /api/artists/scandal/albums/Best Scandal/

+ Response 400 (application/vnd.mason+json)

    The client is trying to send a JSON document that doesn't validate against the schema, or has non-existent release date.

    + Body
    
            {
                "resource_url": "/api/artists/scandal/albums/",
                "@error": {
                    "@message": "Invalid JSON document",
                    "@messages": [                    
                        "'release' is a required property
                        
                        Failed validating 'required' in schema:
                        {'properties': {'discs': {'default': 1,
                        'description': 'Number of discs',
                        'type': 'integer'},
                        'genre': {'description': \"Album's genre(s)\",
                        'type': 'string'},
                        'release': {'description': 'Release date',
                        'pattern': '^[0-9]{4}-[01][0-9]-[0-3][0-9]$',
                        'type': 'string'},
                        'title': {'description': 'Album title',
                        'type': 'string'}},
                        'required': ['title', 'release'],
                        'type': 'object'}
                        
                        On instance:
                        {'title': 'Best Scandal'}"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

+ Response 404 (application/vnd.mason+json)

    The client is trying to add an album for an artist that doesn't exist.

    + Body
    
            {
                "resource_url": "/api/artists/hemuli/albums/",
                "@error": {
                    "@message": "Artist not found",
                    "@messages": [null]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

+ Response 409 (application/vnd.mason+json)

    The client is trying to add an album with a title that's already used by another album for the same artist.

    + Body
    
            {
                "resource_url": "/api/artists/scandal/albums/",
                "@error": {
                    "@message": "Already exists",
                    "@messages": [
                        "Artist 'scandal' already has album with title 'Hello World'"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }
            

+ Response 415 (application/vnd.mason+json)

    The client did not use the proper content type, or the request body was not valid JSON.

    + Body
        
            {
                "resource_url": "/api/artists/scandal/albums/",
                "@error": {
                    "@message": "Unsupported media type",
                    "@messages": [
                        "Use JSON"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error-profile/"
                    }
                }
            }
        
## Albums by Various Artists [/api/artists/VA/albums/]

This is an album collection of collaborative releases aka various artists (VA) albums. For each album only artist and title is included, and artist is listed as "VA". More information can be found by following the `self` relation of each album. VA albums can be added to this collection.

### List albums by various artists [GET]

Gets the list of VA albums known to the API.

+ Relation: albums-va
+ Request

    + Headers
    
            Accept: application/vnd.mason+json
        
+ Response 200 (application/vnd.mason+json)

    + Body
    
            {
                "@namespaces": {
                    "mumeta": {
                        "name": "/musicmeta/link-relations#"
                    }
                },
                "@controls": {
                    "self": {
                        "href": "/api/artists/VA/albums/"
                    },
                    "mumeta:artists-all": {
                        "href": "/api/artists/",
                        "title": "All artists"
                    },
                    "mumeta:albums-all": {
                        "href": "/api/albums/?{sortby}",
                        "title": "All albums",
                        "isHrefTemplate": true,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "sortby": {
                                    "description": "Field to use for sorting",
                                    "type": "string",
                                    "default": "title",
                                    "enum": ["artist", "title", "genre", "release"]
                                }
                            },
                            "required": []
                        }
                    },                    
                    "mumeta:add-album": {
                        "href": "/api/artists/VA/albums/",
                        "title": "Add a new VA album",
                        "encoding": "json",
                        "method": "POST",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "description": "Album title",
                                    "type": "string"
                                },
                                "release": {
                                    "description": "Release date",
                                    "type": "string",
                                    "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]$"
                                },
                                "genre": {
                                    "description": "Album's genre(s)",
                                    "type": "string"
                                },
                                "discs": {
                                    "description": "Number of discs",
                                    "type": "integer",
                                    "default": 1
                                }
                            },
                            "required": ["title", "release"]
                        }
                    }
                },
                "items": [
                    {
                        "title": "Thorns vs Emperor",
                        "artist": "VA",
                        "@controls": {
                            "self": {
                                "href": "/api/artists/VA/albums/Thorns vs Emperor/"
                            },
                            "profile": {
                                "href": "/profiles/album/"
                            }
                        }
                    }
                ]
            }

### Add new various artists album [POST]

Adds a new VA album. The album representation must be valid against the album schema.

+ Relation: add-album
+ Request (application/json)

    + Headers

            Accept: application/vnd.mason+json
        
    + Body
    
            {
                "title": "Transcendental",
                "release": "2015-10-23",
                "genre": "Post-Rock, Atmospheric Sludge Metal",
                "discs": 1
            }

+ Response 201

    + Headers
    
            Location: /api/artists/VA/albums/Transcendental/

+ Response 400 (application/vnd.mason+json)

    The client is trying to send a JSON document that doesn't validate against the schema, or has non-existent release date.

    + Body
    
            {
                "resource_url": "/api/artists/VA/albums/",
                "@error": {
                    "@message": "Invalid date format",
                    "@messages": [
                        "Release date must be written in ISO format (YYYY-MM-DD)"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

+ Response 409 (application/vnd.mason+json)

    The client is trying to add an album with a title that already exists.

    + Body
    
            {
                "resource_url": "/api/artists/VA/albums/",
                "@error": {
                    "@message": "Already exists",
                    "@messages": [
                        "Artist 'VA' already has album with title 'Thorns vs Emperor'"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }
            
+ Response 415 (application/vnd.mason+json)

    The client sent a request with the wrong content type or the request body was not valid JSON.

    + Body
        
            {
                "resource_url": "/api/artists/scandal/albums/",
                "@error": {
                    "@message": "Unsupported media type",
                    "@messages": [
                        "Use JSON"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error-profile/"
                    }
                }
            }

## Album [/api/artists/{artist}/albums/{title}/]

This resource represents an album by a single artist, as identified by the artist's unique name and the albm's title. It includes the list of tracks on the album in addition to the album's own metadata. Individual tracks are usually only visited when modifying their data. They use the [Track Profile](/reference/profiles/track-profile).

+ Parameters

    + artist: scandal (string) - artist's unique name (unique_name)
    + title: Hello World (string) - album's title


### Album information [GET]

Get the album representation.

+ Relation: self
+ Request

    + Headers
    
            Accept: application/vnd.mason+json
        
+ Response 200 (application/vnd.mason+json)

    + Body
    
            {
                "@namespaces": {
                    "mumeta": {
                        "name": "/musicmeta/link-relations#"
                    }
                },
                "title": "Hello World",
                "release": "2014-12-03",
                "genre": "Pop Rock",
                "discs": 1,
                "artist": "Scandal",
                "@controls": {
                    "author": {
                        "href": "/api/artists/scandal/"
                    },
                    "mumeta:albums-by": {
                        "href": "/api/artists/scandal/albums/"
                    },
                    "self": {
                        "href": "/api/artists/scandal/albums/Hello World/"
                    },
                    "profile": {
                        "href": "/profiles/album/"
                    },
                    "collection": {
                        "href": "/api/albums/"
                    },
                    "mumeta:artists-all": {
                        "href": "/api/artists/",
                        "title": "All artists"
                    },
                    "mumeta:add-track": {
                        "href": "/api/artists/scandal/albums/Hello World/",
                        "title": "Add a track to this album",
                        "encoding": "json",
                        "method": "POST",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "description": "Track title",
                                    "type": "string"
                                },
                                "disc_number": {
                                    "description": "Disc number",
                                    "type": "integer",
                                    "default": 1
                                },
                                "track_number": {
                                    "description": "Track number on disc",
                                    "type": "integer"
                                },
                                "length": {
                                    "description": "Track length",
                                    "type": "string",
                                    "pattern": "^:[0-9]{2}:[0-5][0-9]:[0-5][0-9]$"
                                }
                            },
                            "required": ["title", "track_number", "length"]
                        }
                    },
                    "edit": {
                        "href": "/api/artists/scandal/albums/Hello World/",
                        "title": "Edit this album",
                        "encoding": "json",
                        "method": "PUT",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "description": "Album title",
                                    "type": "string"
                                },
                                "release": {
                                    "description": "Release date",
                                    "type": "string",
                                    "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]$"
                                },
                                "genre": {
                                    "description": "Album's genre(s)",
                                    "type": "string"
                                },
                                "discs": {
                                    "description": "Number of discs",
                                    "type": "integer",
                                    "default": 1
                                }
                            },
                            "required": ["title", "release"]
                        }
                    },
                    "mumeta:delete": {
                        "href": "/api/artists/scandal/albums/Hello World/",
                        "title": "Delete this album",
                        "method": "DELETE"
                    }
                },
                "items": [
                    {
                        "title": "Image",
                        "length": "00:04:26",
                        "disc_number": 1,
                        "track_number": 1,
                        "@controls": {
                            "self": {
                                "href": "/api/artists/scandal/albums/Hello World/1/1/"
                            },
                            "profile": {
                                "href": "/profiles/track/"
                            }
                        }
                    }
                ]
            }

+ Response 404 (application/vnd.mason+json)

    The client is trying to access an album that doesn't exist (either due to non-existent artist or album).

    + Body
    
            {
                "resource_url": "/api/artists/scandal/albums/Yellow/",
                "@error": {
                    "@message": "Album not found",
                    "@messages": [null]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }
            
### Add track to album [POST]

Adds a new track to the album. The track representation must be valid against the track schema. Also its position on the album (combination of disc number and track number) must be unoccupied.

+ Relation: add-track
+ Request (application/json)

    + Headers
    
            Accept: application/vnd.mason+json
        
    + Body
    
            {
                "title": "Your Song",
                "disc_number": 1,
                "track_number": 2,
                "length": "00:03:43"
            }

+ Response 201

    + Headers
    
            Location: /api/artists/scandal/albums/Hello World/1/2/
            
    + Body
    
            {}
            


+ Response 400 (application/vnd.mason+json)

    The client is trying to send a JSON document that doesn't validate against the schema.

    + Body
    
            {
                "resource_url": "/api/artists/scandal/albums/Hello World/",
                "@error": {
                    "@message": "Invalid JSON document",
                    "@messages": [
                        "'3:43' does not match '^[0-9]{2}:[0-5][0-9]:[0-5][0-9]$'
                        
                        Failed validating 'pattern' in schema['properties']['length']:
                        {'description': 'Track length',
                        'pattern': '^[0-9]{2}:[0-5][0-9]:[0-5][0-9]$',
                        'type': 'string'}
                        
                        On instance
                        ['length']: '3:43'"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error-profile/"
                    }
                }
            }

+ Response 404 (application/vnd.mason+json)

    The client is trying to add a track to an album that doesn't exist (due to non-existent artist or album).

    + Body
    
            {
                "resource_url": "/api/artists/scandal/albums/Yellow/",
                "@error": {
                    "@message": "Album not found",
                    "@messages": [null]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

+ Response 409 (application/vnd.mason+json)

    The client is trying to add a track with a combination of disc and track numbers that is already occupied.

    + Body
    
            {
                "resource_url": "/api/artists/scandal/albums/Hello World/",
                "@error": {
                    "@message": "Already exists",
                    "@messages": [
                        "Album 'Hello World' already has a track at 1.1"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

            
+ Response 415 (application/vnd.mason+json)

    The client sent a request with the wrong content type or the request body was not valid JSON.

    + Body
        
            {
                "resource_url": "/api/artists/scandal/albums/Hello World/",
                "@error": {
                    "@message": "Unsupported media type",
                    "@messages": [
                        "Use JSON"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error-profile/"
                    }
                }
            }

### Edit album information [PUT]

Replace the album's representation with a new one. Missing optinal fields will be set to null. Must validate against the album schema. 

+ Relation: edit
+ Request (application/json)

    + Headers
        
            Accept: application/vnd.mason+json
        
    + Body
    
            {
                "title": "Hello World",
                "release": "2014-12-03",
                "genre": "Pop Rock, Power Pop",
                "discs": 1
            }
        
+ Response 204


+ Response 400 (application/vnd.mason+json)

    The client is trying to send a JSON document that doesn't validate against the schema, or has non-existent release date.

    + Body
    
            {
                "resource_url": "/api/artists/scandal/albums/Hello World/",
                "@error": {
                    "@message": "Invalid date format",
                    "@messages": [
                        "Release date must be written in ISO format (YYYY-MM-DD)"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

+ Response 404 (application/vnd.mason+json)

    The client is trying to edit an album that doesn't exist (due to non-existent artist or album). 

    + Body
    
            {
                "resource_url": "/api/artists/scandal/albums/Yellow/",
                "@error": {
                    "@message": "Album not found",
                    "@messages": [null]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }
            
+ Response 409 (application/vnd.mason+json)

    The client is trying to change the album's title to a one that is already in use for the artist.

    + Body
    
            {
                "resource_url": "/api/artists/scandal/albums/Honey/",
                "@error": {
                    "@message": "Title reserved",
                    "@messages": [
                        "Artist 'scandal' already has another album with title 'Hello World'"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }
        
+ Response 415 (application/vnd.mason+json)

    The client sent a request with the wrong content type or the request body was not valid JSON.

    + Body
        
            {
                "resource_url": "/api/artists/scandal/albums/Hello World/",
                "@error": {
                    "@message": "Unsupported media type",
                    "@messages": [
                        "Use JSON"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error-profile/"
                    }
                }
            }

### Delete album [DELETE]

Deletes the album, and all associated tracks.

+ Relation: delete
+ Request

    + Headers
        
            Accept: application/vnd.mason+json
        
+ Response 204

+ Response 404 (application/vnd.mason+json)

    The client is trying to delete an album that doesn't exist (due to non-existent artist or album). 

    + Body
    
            {
                "resource_url": "/api/artists/scandal/albums/Yellow/",
                "@error": {
                    "@message": "Album not found",
                    "@messages": [null]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

## Various Artists Album [/api/artists/VA/albums/{title}/]

This resource represents an album by multiple artists, as identified by the album's title. It includes the list of tracks on the album in addition to the album's own metadata. Individual tracks are usually only visited when modifying their data. They use the [Track Profile](/reference/profiles/track-profile).

+ Parameters

    + title: 'Thorns vs Emperor' (string) - album's title


### Album information [GET]

Get the album's representation.

+ Relation: self
+ Request

    + Headers
    
            Accept: application/vnd.mason+json
        
+ Response 200 (application/vnd.mason+json)
 
    + Body
    
            {
                "@namespaces": {
                    "mumeta": {
                        "name": "/musicmeta/link-relations#"
                    }
                },
                "title": "Thorns vs Emperor",
                "release": "1999-01-01",
                "genre": "Black Metal",
                "discs": 1,
                "artist": "VA",
                "@controls": {
                    "mumeta:albums-va": {
                        "href": "/api/artists/VA/albums/",
                        "title": "All VA albums"
                    },
                    "self": {
                        "href": "/api/artists/VA/albums/Thorns vs Emperor/"
                    },
                    "profile": {
                        "href": "/profiles/album/"
                    },
                    "collection": {
                        "href": "/api/albums/"
                    },
                    "mumeta:artists-all": {
                        "href": "/api/artists/",
                        "title": "All artists"
                    },
                    "mumeta:add-track": {
                        "href": "/api/artists/VA/albums/Thorns vs Emperor/",
                        "title": "Add a track to this album",
                        "encoding": "json",
                        "method": "POST",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "description": "Track title",
                                    "type": "string"
                                },
                                "disc_number": {
                                    "description": "Disc number",
                                    "type": "integer",
                                    "default": 1
                                },
                                "track_number": {
                                    "description": "Track number on disc",
                                    "type": "integer"
                                },
                                "length": {
                                    "description": "Track length",
                                    "type": "string",
                                    "pattern": "^:[0-9]{2}:[0-5][0-9]:[0-5][0-9]$"
                                },
                                "va_artist": {
                                    "description": "Track artist unique name (mandatory on VA albums)",
                                    "type": "string"
                                }
                            },
                            "required": ["title", "track_number", "length", "va_artist"]
                        }
                    },
                    "edit": {
                        "href": "/api/artists/VA/albums/Thorns vs Emperor/",
                        "title": "Edit this album",
                        "encoding": "json",
                        "method": "PUT",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "description": "Album title",
                                    "type": "string"
                                },
                                "release": {
                                    "description": "Release date",
                                    "type": "string",
                                    "pattern": "^[0-9]{4}-[01][0-9]-[0-3][0-9]$"
                                },
                                "genre": {
                                    "description": "Album's genre(s)",
                                    "type": "string"
                                },
                                "discs": {
                                    "description": "Number of discs",
                                    "type": "integer",
                                    "default": 1
                                }
                            },
                            "required": ["title", "release"]
                        }
                    },
                    "mumeta:delete": {
                        "href": "/api/artists/VA/albums/Thorns vs Emperor/",
                        "title": "Delete this album",
                        "method": "DELETE"
                    }
                },
                "items": [
                    {
                        "title": "Exördium",
                        "length": "00:03:00",
                        "disc_number": 1,
                        "track_number": 1,
                        "va_artist": "Emperor",
                        "@controls": {
                            "self": {
                                "href": "/api/artists/VA/albums/Thorns vs Emperor/1/1/"
                            },
                            "profile": {
                                "href": "/profiles/track/"
                            }
                        }
                    },
                    {
                        "title": "Aerie Descent",
                        "length": "00:08:34",
                        "disc_number": 1,
                        "track_number": 2,
                        "va_artist": "Thorns",
                        "@controls": {
                            "self": {
                                "href": "/api/artists/VA/albums/Thorns vs Emperor/1/2/"
                            },
                            "profile": {
                                "href": "/profiles/track/"
                            }
                        }
                    }
                ]
            }

+ Response 404 (application/vnd.mason+json)

    The client is trying to get an album that doesn't exist.

    + Body
    
            {
                "resource_url": "/api/artists/VA/albums/Transcendental/",
                "@error": {
                    "@message": "Album not found",
                    "@messages": [null]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

            
### Add track to album [POST]

Adds a new track to the album. The track representation must be valid against the track schema. Also its position on the album (combination of disc number and track number) must be unoccupied. Note that VA tracks have the additional required field `va_artist` which indicates the track's author.

+ Relation: add-track
+ Request (application/json)

    + Headers
    
            Accept: application/vnd.mason+json
        
    + Body
    
            {
                "title": "I am",
                "disc_number": 1,
                "track_number": 3,
                "length": "00:05:04",
                "va_artist": "emperor"
            }

+ Response 201

    + Headers
    
            Location: /api/artists/VA/albums/Thorns vs Emperor/1/2/


+ Response 400 (application/vnd.mason+json)

    The client is trying to send a JSON document that doesn't validate against the schema.

    + Body
    
            {
                "resource_url": "/api/artists/VA/albums/Thorns vs Emperor/",
                "@error": {
                    "@message": "Invalid JSON document",
                    "@messages": [
                        "'5:04' does not match '^[0-9]{2}:[0-5][0-9]:[0-5][0-9]$'
                        
                        Failed validating 'pattern' in schema['properties']['length']:
                        {'description': 'Track length',
                        'pattern': '^[0-9]{2}:[0-5][0-9]:[0-5][0-9]$',
                        'type': 'string'}
                        
                        On instance
                        ['length']: '5:04'"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error-profile/"
                    }
                }
            }

+ Response 404 (application/vnd.mason+json)

    The client is trying to add a track for an album that doesn't exist.

    + Body
    
            {
                "resource_url": "/api/artists/VA/albums/Xenogears/",
                "@error": {
                    "@message": "Album not found",
                    "@messages": [null]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }
        
+ Response 409 (application/vnd.mason+json)

    The client is trying to add a track with a combination of disc and track numbers that is already occupied.

    + Body
    
            {
                "resource_url": "/api/artists/VA/albums/Thorns vs Emperor/",
                "@error": {
                    "@message": "Already exists",
                    "@messages": [
                        "Album 'Thorns vs Emperor' already has a track at 1.1"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }
        
+ Response 415 (application/vnd.mason+json)

    The client sent a request with the wrong content type or the request body was not valid JSON.

    + Body
        
            {
                "resource_url": "/api/artists/VA/albums/Thorns vs Emperor/",
                "@error": {
                    "@message": "Unsupported media type",
                    "@messages": [
                        "Use JSON"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error-profile/"
                    }
                }
            }

### Edit album information [PUT]

Replace the album's representation with a new one. Missing optinal fields will be set to null. Must validate against the album schema. 

+ Relation: edit
+ Request (application/json)

    + Headers
        
            Accept: application/vnd.mason+json
        
    + Body
    
            {
                "title": "Thorns vs Emperor",
                "release": "1999-01-01",
                "genre": "Industrial Black Metal",
                "discs": 1
            }
        
+ Response 204

+ Response 400 (application/vnd.mason+json)

    The client is trying to send a JSON document that doesn't validate against the schema, or has non-existent release date.

    + Body
    
            {
                "resource_url": "/api/artists/VA/albums/Thorns vs Emperor/",
                "@error": {
                    "@message": "Invalid date format",
                    "@messages": [
                        "Release date must be written in ISO format (YYYY-MM-DD)"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

+ Response 404 (application/vnd.mason+json)

    The client is trying to modify an album that doesn't exist.

    + Body
    
            {
                "resource_url": "/api/artists/VA/albums/Transcendental/",
                "@error": {
                    "@message": "Album not found",
                    "@messages": [null]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }
            
+ Response 409 (application/vnd.mason+json)

    The client is trying to change the title to a one that is already in use.

    + Body
    
            {
                "resource_url": "/api/artists/VA/albums/Yogsothery/",
                "@error": {
                    "@message": "Title reserved",
                    "@messages": [
                        "Artist 'VA' already has another album with title 'Thorns vs Emperor'"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }
        
+ Response 415 (application/vnd.mason+json)

    The client sent a request with the wrong content type or the request body was not valid JSON.

    + Body
        
            {
                "resource_url": "/api/artists/VA/albums/Thorns vs Emperor/",
                "@error": {
                    "@message": "Unsupported media type",
                    "@messages": [
                        "Use JSON"
                    ]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error-profile/"
                    }
                }
            }

### Delete album [DELETE]

+ Relation: delete
+ Request

    + Headers
        
            Accept: application/vnd.mason+json
        
+ Response 204

+ Response 404 (application/vnd.mason+json)

    The client is trying to delete an album that doesn't exist.

    + Body
    
            {
                "resource_url": "/api/artists/VA/albums/Transcendental/",
                "@error": {
                    "@message": "Album not found",
                    "@messages": [null]
                },
                "@controls": {
                    "profile": {
                        "href": "/profiles/error/"
                    }
                }
            }

