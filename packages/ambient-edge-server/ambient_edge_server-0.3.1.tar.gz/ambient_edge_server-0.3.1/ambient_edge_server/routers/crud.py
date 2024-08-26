from ambient_backend_api_client import Node
from fastapi import APIRouter, Depends, HTTPException

from ambient_edge_server.services import crud_service, service_manager

router = APIRouter(prefix="/data", tags=["data", "nodes"])


# GET node data
@router.get("/node", response_model=Node)
async def get_node_data(
    crud_service: crud_service.CRUDService = Depends(
        service_manager.svc_manager.get_crud_service
    ),
):
    node_data = await crud_service.get_node_data()
    if not node_data:
        raise HTTPException(status_code=404, detail="Node data not found")
    return node_data


# PUT node data
@router.put("/node", response_model=Node)
async def update_node_data(
    crud_service: crud_service.CRUDService = Depends(
        service_manager.svc_manager.get_crud_service
    ),
):
    node_data = await crud_service.update_node_data()
    return node_data


# DELETE node data
@router.delete("/node")
async def delete_node_data(
    crud_service: crud_service.CRUDService = Depends(
        service_manager.svc_manager.get_crud_service
    ),
):
    await crud_service.clear_node_data()
    return {"message": "Node data deleted"}
