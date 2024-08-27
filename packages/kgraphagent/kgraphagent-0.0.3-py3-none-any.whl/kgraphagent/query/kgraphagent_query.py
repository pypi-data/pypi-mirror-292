
class KGraphAgentQuery:
    pass

# base class for queries

# query functions meant to be wrapped in an LLM function call
# for particular agent implementations using libraries such as langchain, llamaindex

# queries may simply wrap existing query methods defined in kgservice like for kgframe
# or may define queries using objects/functions from kgservice

# query functions are meant to be applied to the underlying kgservice for a
# graph/vector database query or applied to kgmemory for an in-memory graph/vector query



