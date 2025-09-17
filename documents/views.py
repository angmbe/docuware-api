from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from utils.responses import standard_response
from .models import Document
from .serializers import DocumentSerializer


class DocumentListCreateView(APIView):
    def get(self, request):
        """Obtener todos los documentos"""
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        #return Response(serializer.data, status=status.HTTP_200_OK)
        return standard_response(
            success=True,
            message="Documentos obtenidos correctamente",
            data=serializer.data,
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
