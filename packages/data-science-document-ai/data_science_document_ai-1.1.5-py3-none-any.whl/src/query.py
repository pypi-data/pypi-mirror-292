"""Contains queries logic."""
from src.io import query_dwh


def query_document_id(params, role=None):
    """Query data from DWH."""
    # Select the latest FinalHbL if role is finalHbL
    if role == "finalHbL":
        doc_role = f"(document_type_code = 'finalHbL' AND row_number = 1)"
    else:
        doc_role = f"document_type_code IN ('{role}')"

    query = f"""SELECT s.shipment_id, container_type_count, curr.doc_ids,

                    FROM `{params['gbq_db_schema_g']}.{params['gbq_db_table_g']}` s   # noqa

                    JOIN (
                        SELECT
                          shipment_id,
                          -- consider all commercialInvoice, packingList, and ONLY the latest finalHbL
                          STRING_AGG(CASE WHEN {doc_role}   # noqa
                                          THEN document_id END, '|' ORDER BY document_id) AS doc_ids
                        FROM (
                            SELECT *,
                                ROW_NUMBER() OVER (PARTITION BY shipment_id, document_type_code
                                                    ORDER BY created_at DESC) as row_number
                            FROM `{params['gbq_db_schema_s']}.{params['gbq_db_table_s']}`   # noqa
                            WHERE document_type_code IN ('{role}')
                            ) as eligible_docs
                        GROUP BY shipment_id
                        ) curr using (shipment_id)

                    WHERE transport_type = 'fcl'
                    AND trade_class_code = 'EU Imp'
                    AND total_containers >= 1
                    AND booked_at between '2023-08-01' and '2023-12-31'
                    AND doc_ids is not null """  # noqa

    return query_dwh(params, query)


def query_combined_ci_pl_document_id(params):
    """A special query from DWH for commercialInvoiceAndPackingList documents."""

    query = f"""with ranked_shipments as(
                SELECT s.shipment_id, shipper_contact_company_name, container_type_count, curr.doc_ids,
                        ROW_NUMBER() OVER (PARTITION BY s.shipper_contact_company_name ORDER BY s.shipment_id) AS row_num
                                    FROM `gold.gsc_shipments` s   # noqa
                
                                    JOIN (
                                        SELECT
                                          shipment_id,
                                          STRING_AGG(CASE WHEN document_type_code IN ('commercialInvoiceAndPackingList')   # noqa
                                                          THEN document_id END, '|' ORDER BY document_id) AS doc_ids
                                        FROM (
                                            SELECT *,
                                                ROW_NUMBER() OVER (PARTITION BY shipment_id, document_type_code
                                                                    ORDER BY created_at DESC) as row_number
                                            FROM `sem__common.shipment_provided_documents`   # noqa
                                            WHERE document_type_code IN ('commercialInvoiceAndPackingList')
                                            and state = 'published'
                                            and mime_type = 'application/pdf'
                                            and created_at between '2024-06-01' and '2024-06-14'
                                            ) as eligible_docs
                                        GROUP BY shipment_id
                                        ) curr using (shipment_id)
                
                                    --  transport_type = 'fcl'
                                    -- AND trade_class_code = 'EU Imp'
                                    -- AND total_containers >= 1
                                    WHERE doc_ids is not null)
                
                select * from ranked_shipments
                where row_num <= 4
                order by shipment_id"""  # noqa

    return query_dwh(params, query)
