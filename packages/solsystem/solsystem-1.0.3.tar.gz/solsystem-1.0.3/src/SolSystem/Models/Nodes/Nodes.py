from pydantic.alias_generators import to_camel
from pydantic import (
    BaseModel,
    ConfigDict,
)
from SolSystem.Models.Common import (
    UInt32,
    UInt16,
    PublicKey,
)



class ClusterNode(BaseModel):
    """### Summary
    Information on a node participatin gin a clsuter
    
    ### Parameters
    `pubkey:` Node public key

    `gossip:` Gossip network address for the node

    `tpu:` TPU network address for the node

    `rpc:` JSON RPC network address for the node

    `version:` The software version of the node, or null if the version
    information is not available

    `feature_set:` The unique identifier of the node's feature set

    `shared_version:` The shred version the node has been configured to use"""
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name = True,
    )

    pubkey: PublicKey
    gossip: str | None = None
    tpu: str | None = None
    rpc: str | None = None
    version: str | None = None
    feature_set: UInt32 | None = None
    shared_version: UInt16 | None = None



class NodeVersion(BaseModel):
    """### Parameters
    `solana_core:` Software version of solana-core

    `feature_set:` Unique identifier of the current software's feature set"""
    model_config = ConfigDict(
        alias_generator = lambda s: s.replace("_","-"),
        populate_by_name = True,
    )

    solana_core: str
    feature_set: UInt32



class NodeIdentity(BaseModel):
    """### Parameters
    `identity:` Address of the node"""
    identity: PublicKey