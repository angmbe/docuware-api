from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from utils.responses import standard_response
from .models import Document, PurchaseOrder, TipoDocumento
from .serializers import (
    DocumentSerializer,
    PurchaseOrderSerializer,
    TipoDocumentoSerializer,
)

class TipoDocumentoView(APIView):
    def get(self, request):
        tipos = TipoDocumento.objects.all()
        serializer = TipoDocumentoSerializer(tipos, many=True)
        return standard_response(
            success=True,
            message="Tipos de documento obtenidos correctamente",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


class DocumentListCreateView(APIView):
    def get(self, request):
        """Obtener todos los documentos"""
        documents = Document.objects.all().order_by('-documentid')
        # 2️⃣ Agrupar por las columnas clave y contar
        duplicates = (
            Document.objects
            .values('documentserial', 'documentnumber', 'suppliernumber')
            .annotate(count=Count('documentid'))
            .filter(count__gt=1)
        )

        # 3️⃣ Crear un conjunto para rápida búsqueda
        duplicate_keys = {
            (item['documentserial'], item['documentnumber'], item['suppliernumber'])
            for item in duplicates
        }

        # 4️⃣ Serializar los datos
        serializer = DocumentSerializer(documents, many=True)
        serialized_data = serializer.data

        # 5️⃣ Agregar campo "isDuplicated"
        for doc in serialized_data:
            key = (doc.get('documentserial'), doc.get('documentnumber'), doc.get('suppliernumber'))
            doc["isDuplicated"] = "X" if key in duplicate_keys else ""

        # 6️⃣ Retornar respuesta estándar
        return standard_response(
            success=True,
            message="Documentos obtenidos correctamente",
            data=serialized_data,
            status_code=status.HTTP_200_OK
        )


    def post(self, request):
        """Crear un nuevo documento"""
        data = request.data.copy()
        data["created_at"] = timezone.now()

        serializer = DocumentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            #return Response(serializer.data, status=status.HTTP_201_CREATED)
            return standard_response(
            success=True,
            message="Document created successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class DocumentDeleteView(APIView):
    def post(self, request):
        document_id = request.data.get("documentid")

        # Validar que se haya enviado el ID
        if not document_id:
            return Response(
                {"error": "El campo 'documentid' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            document = Document.objects.get(documentid=document_id)
            document.delete()

            return Response(
                {"message": f"Documento con ID {document_id} eliminado correctamente."},
                status=status.HTTP_200_OK
            )

        except Document.DoesNotExist:
            return Response(
                {"error": f"No se encontró ningún documento con documentid={document_id}."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PurchaseOrderCreateView(APIView):
    def post(self, request):
        serializer = PurchaseOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return standard_response(
                success=True,
                message="Orden de compra creada correctamente",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )

        return standard_response(
            success=False,
            message="Error al crear la orden de compra",
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class PurchaseOrderDetailView(APIView):
    def get(self, request, pk):
        try:
            purchase_order = PurchaseOrder.objects.prefetch_related("details").get(
                purchaseOrderID=pk
            )
        except PurchaseOrder.DoesNotExist:
            return standard_response(
                success=False,
                message="Orden de compra no encontrada",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = PurchaseOrderSerializer(purchase_order)
        return standard_response(
            success=True,
            message="Orden de compra obtenida correctamente",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

class DocumentDetailView(APIView):
    def get(self, request, pk):
        """Obtener un documento por ID"""
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentSerializer(document)
        #return Response(serializer.data, status=status.HTTP_200_OK)
        return standard_response(
            success=True,
            message="List documents successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )


    def patch(self, request, pk):
        """Actualizar un documento"""
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            #return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
            return standard_response(
            success=False,
            message="Documento no encontrado",
            status_code=status.HTTP_404_NOT_FOUND
        )

        data = request.data.copy()
        data["updated_at"] = timezone.now()

        serializer = DocumentSerializer(document, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            #return Response(serializer.data, status=status.HTTP_200_OK)
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return standard_response(
            success=True,
            message="Document updated correctly",
            data=serializer.data
            )
        return standard_response(
        success=False,
        message="Error while updating document",
        data=serializer.errors,
        status_code=status.HTTP_400_BAD_REQUEST
    )


    def delete(self, request, pk):
        """Eliminar un documento"""
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        document.delete()
        return Response({"message": "Document deleted"}, status=status.HTTP_204_NO_CONTENT)
