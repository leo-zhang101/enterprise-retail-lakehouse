{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name in ['staging', 'intermediate', 'marts'] -%}
        {{ custom_schema_name }}
    {%- else -%}
        {{ default_generate_schema_name(custom_schema_name, node) }}
    {%- endif -%}
{%- endmacro %}
