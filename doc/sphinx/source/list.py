all = (
    "code/Borg",
    "code/Callbacks",
    "code/CliParse",
    "code/CommandHelper7z",
    "code/CreateObjects",
    "code/DisplayState",
    "code/Events",
    "code/ImageDisplay",
    "code/ImageDisplayWidget",
    "code/__init__",
    "code/IO",
    "code/JsonDict",
    "code/KeyBindings",
    "code/Logger",
    "code/MainWindow",
    "code/Mime",
    "code/Notifications",
    "code/PathIndex",
    "code/PathNodeAbstract",
    "code/PathNodeExceptions",
    "code/PathNodeFactory",
    "code/PathNodeStoreExceptions",
    "code/PathNodeStore",
    "code/Persistence",
    "code/Platform",
    "code/Plugins",
    "code/PluginsStore",
    "code/ProgressivePixbufLoader",
    "code/PytheiaGui",
    "code/RarItemCacheable",
    "code/Rar",
    "code/SampleStats",
    "code/Screen",
    "code/SourceImage",
    "code/SupportingPool",
    "code/tarfile_extras",
    "code/TarItemCacheable",
    "code/Tar",
    "code/ThumbnailsView",
    "code/TreeStore",
    "code/Utils",
    "code/Widgets",
    "code/ZipItemCacheable",
    "code/Zip",
)

for i in all:
    print("-----------------")
    print(i)

    m = i.split("/")[1]
    stars = "".join(["*" for j in m])
    t = """
%s
%s

.. automodule:: %s
   :members:
   :undoc-members:

""" % (m, stars, m)
    with open(i + ".rst", "wb") as f:
        f.write(bytes(t, "UTF-8"))
