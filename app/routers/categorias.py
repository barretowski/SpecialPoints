from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_usuario_atual, requer_responsavel
from app.models.categoria_tarefa import CategoriaTarefa
from app.models.usuario import Usuario
from app.schemas.categoria_tarefa import AtualizarCategoriaInput, CategoriaPublica, CriarCategoriaInput

router = APIRouter(prefix="/categorias", tags=["Categorias de Tarefas"])


@router.post("/", response_model=CategoriaPublica, status_code=status.HTTP_201_CREATED)
async def criar_categoria(
    dados: CriarCategoriaInput,
    _: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(CategoriaTarefa).where(CategoriaTarefa.nome == dados.nome))
    if resultado.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Categoria já existe")

    categoria = CategoriaTarefa(**dados.model_dump())
    db.add(categoria)
    await db.commit()
    await db.refresh(categoria)
    return categoria


@router.get("/", response_model=list[CategoriaPublica])
async def listar_categorias(
    _: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(CategoriaTarefa).order_by(CategoriaTarefa.nome))
    return resultado.scalars().all()


@router.patch("/{categoria_id}", response_model=CategoriaPublica)
async def atualizar_categoria(
    categoria_id: int,
    dados: AtualizarCategoriaInput,
    _: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(CategoriaTarefa).where(CategoriaTarefa.id == categoria_id))
    categoria = resultado.scalar_one_or_none()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")

    for campo, valor in dados.model_dump(exclude_none=True).items():
        setattr(categoria, campo, valor)

    await db.commit()
    await db.refresh(categoria)
    return categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_categoria(
    categoria_id: int,
    _: Usuario = Depends(requer_responsavel()),
    db: AsyncSession = Depends(get_db),
):
    resultado = await db.execute(select(CategoriaTarefa).where(CategoriaTarefa.id == categoria_id))
    categoria = resultado.scalar_one_or_none()
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")

    await db.delete(categoria)
    await db.commit()
