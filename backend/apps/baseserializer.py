# core/base_serializer.py
from rest_framework import serializers

class BaseRulesSerializer(serializers.ModelSerializer):
    """
    Centralized Serializer for Validation.
    Define RULES in your serializer to automatically validate fields.
    RULES = {
        "field_name": [(validator_fn, arg1, arg2), (validator_fn2, )]
    }
    """
    RULES = {} 

    def validate(self, attrs):
        errors = {}

        # Validate defined RULES
        for field, rules in self.RULES.items():
            # If field is not in attrs, check instance for partial updates or default
            value = attrs.get(field)
            
            # Check if this is a partial update and field is missing
            if self.partial and field not in attrs:
                 # Should we validate existing value? 
                 # Usually validation runs on incoming data. 
                 # If 'required' is a rule, it should fail if missing in creation.
                 # But if partial update, we might skip if not provided.
                 # Let's assume rules apply to present data or required checks.
                 # If value is missing and required rule exists, we should check it.
                 pass

            for rule in rules:
                fn = rule[0]
                args = rule[1:]
                try:
                    fn(value, *args)
                except serializers.ValidationError as e:
                    # Capturing the error message
                    detail = e.detail
                    if isinstance(detail, list):
                        errors[field] = detail
                    elif isinstance(detail, dict):
                         errors[field] = [str(val) for val in detail.values()]
                    else:
                        errors[field] = [str(detail)]
                    break  # Stop at first error for this field

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
