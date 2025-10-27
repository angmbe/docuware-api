from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from documents.models import Document  # ← importa desde la app correcta
from .models import DocumentDetail
from .serializers import DocumentDetailSerializer, DocumentFullSerializer

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


class DocumentFullView(APIView):
    def get(self, request):
        try:
            documents = Document.objects.all()
            details = DocumentDetail.objects.all()
            merged_data = []

            for doc in documents:
                # Filtrar los detalles relacionados con este documento
                matched_details = details.filter(
                    suppliernumber=doc.suppliernumber,
                    documentserial=doc.documentserial,
                    documentnumber=doc.documentnumber
                )

                # Manejo seguro del centro de costo
                centercost_desc = ""
                if doc.centercost:
                    centercost_desc = f"{doc.centercost.centrocodigo} - {doc.centercost.descripcion}"


                if matched_details.exists():
                    for det in matched_details:
                        merged_data.append({
                            "documenttype": doc.documenttype.tipo or "",
                            "suppliernumber": doc.suppliernumber or "",
                            "documentserial": doc.documentserial or "",
                            "documentnumber": doc.documentnumber or "",
                            "documentdate": doc.documentdate,
                            "suppliername": doc.suppliername or "",
                            "description": det.description or "",
                            "vehicle_nro": det.vehicle_no or "",
                            "driver" : doc.driver or "",
                            "centercost" : centercost_desc,
                            "unit_measure_description": det.unit_measure_description or "",
                            "quantity": det.quantity,
                            "currency": doc.currency,
                            "unit_value": det.unit_value,
                            #"tax_value": det.tax_value,
                            "total_value": det.total_value,
                            "amount": doc.amount,
                            "taxamount": doc.taxamount,
                            "totalamount": doc.totalamount,
                        })
                else:
                    # Si no tiene detalles, igual devolvemos la cabecera
                    merged_data.append({
                        "documenttype": doc.documenttype.tipo or "",
                        "suppliernumber": doc.suppliernumber or "",
                        "documentserial": doc.documentserial or "",
                        "documentnumber": doc.documentnumber or "",
                        "documentdate": doc.documentdate,
                        "suppliername": doc.suppliername,
                        "description": "",
                        "vehicle_nro": "",
                        "driver" : doc.driver or "",
                        "centercost" : centercost_desc,
                        "unit_measure_description": "",
                        "quantity": None,
                        "currency": doc.currency,
                        "unit_value": None,
                        #"tax_value": None,
                        "total_value": None,
                        "amount": doc.amount,
                        "taxamount": doc.taxamount,
                        "totalamount": doc.totalamount,
                    })

            return Response(merged_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)