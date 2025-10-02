from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DocumentDetail
from .serializers import DocumentDetailSerializer

class DocumentDetailView(APIView):
    # GET con supplierNumber, documentSerial, documentNumber
    def get(self, request):
        supplier_number = request.query_params.get("suppliernumber")
        document_serial = request.query_params.get("documentserial")
        document_number = request.query_params.get("documentnumber")

        # Validación: todos son obligatorios
        if not (supplier_number and document_serial and document_number):
            return Response(
                {"error": "suppliernumber, documentserial y documentnumber son obligatorios"},
                status=status.HTTP_400_BAD_REQUEST
            )

        details = DocumentDetail.objects.filter(
            suppliernumber=supplier_number,
            documentserial=document_serial,
            documentnumber=document_number
        )

        serializer = DocumentDetailSerializer(details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST para crear
    def post(self, request):
        serializer = DocumentDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT para actualizar (por id)
    def put(self, request, pk=None):
        try:
            detail = DocumentDetail.objects.get(pk=pk)
        except DocumentDetail.DoesNotExist:
            return Response({"error": "Registro no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentDetailSerializer(detail, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
