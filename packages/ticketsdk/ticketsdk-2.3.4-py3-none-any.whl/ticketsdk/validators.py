from marshmallow import RAISE, Schema, ValidationError, fields


class NewTicketSchema(Schema):
    issue_code = fields.Str(required=True)
    from_system = fields.Str(required=True)
    ref_code = fields.Str(required=True)
    partner_code = fields.Str(required=False, allow_none=True, allow_empty=True)
    ticket_name = fields.Str(required=True)
    requested_email = fields.Str(required=True)
    ticket_description = fields.Str(required=True)
    attachments = fields.List(fields.Str(), allow_none=False, allow_empty=True)
    lambda_type = fields.Str(required=True)
    requested_by_employee_email = fields.Str(required=False)
    requested_by_employee_name = fields.Str(required=False)

    class Meta:
        strict = True
        unknown = RAISE


class NewSellerSchema(Schema):
    partner_code = fields.Str(required=True)
    email = fields.Str(required=True)
    cs_email = fields.Str(required=False)
    lambda_type = fields.Str(required=True)
    name = fields.Str(required=False)
    company_name = fields.Str(required=False)

    class Meta:
        strict = True
        unknown = RAISE


class ListTicketSchema(Schema):
    lambda_type = fields.Str(required=True)
    page = fields.Int(required=True)
    code = fields.Str(required=False)
    created_at_from = fields.Float(required=False)
    created_at_to = fields.Float(required=False)
    page = fields.Int(required=False)
    status = fields.Str(required=False)
    partner_code = fields.Str(required=False)
    refcode = fields.Str(required=False)
    from_system = fields.Str(required=False)

    class Meta:
        strict = True
        unknown = RAISE


class DetailTicketSchema(Schema):
    lambda_type = fields.Str(required=True)
    ticket_id = fields.Int(required=True)

    class Meta:
        strict = True
        unknown = RAISE


class DetailCommentTicketSchema(Schema):
    lambda_type = fields.Str(required=True)
    ticket_id = fields.Int(required=True)

    class Meta:
        strict = True
        unknown = RAISE


class CreateCommentTicketSchema(Schema):
    lambda_type = fields.Str(required=True)
    ticket_id = fields.Int(required=True)
    content = fields.Str(required=True)
    attachments = fields.List(fields.Str(), allow_none=True, allow_empty=True)
    partner_code = fields.Str(required=True)
    created_by_employee_email = fields.Str(required=False)
    created_by_employee_name = fields.Str(required=False)

    class Meta:
        strict = True
        unknown = RAISE
