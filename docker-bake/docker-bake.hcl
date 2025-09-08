group "mongo-schema" {
    targets = ["exporter", "importer"]
}

target "exporter" {
    context = "../"
    dockerfile = "../dockerfile-exporter"
    tags =  ["mongo-schema-exporter:latest"]

}
target "importer" {
    context = "../"
    dockerfile = "../dockerfile-importer"
    tags = ["mongo-schama-importer:latest"]
}

target "list" {
  context = "../"
  dockerfile = "../dockerfile-list"
  tags = [ "mongo-schema-list"] 
}