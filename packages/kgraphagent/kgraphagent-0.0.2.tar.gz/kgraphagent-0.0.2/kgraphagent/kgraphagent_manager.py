
class KGraphAgentManager:
    pass

# manager class for agents utilizing knowledge graphs
# queries can be used with kgraphservice and kgraphmemory

# this library is agnostic with regard to libraries used to implement agents
# such as langchain and llamaindex

# such a library may use kgraphagent as a dependency in its implementation or
# an agent implementation may use such a library and wrap the functionality in
# this library

# handle unpacking containers of kg message history
# may use data definitions in kgraphservice, such as message part

