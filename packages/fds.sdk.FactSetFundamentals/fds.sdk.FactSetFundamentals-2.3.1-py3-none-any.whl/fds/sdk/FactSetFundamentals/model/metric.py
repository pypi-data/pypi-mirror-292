"""
    FactSet Fundamentals API

    Gain access to current, comprehensive, and comparative information on securities in worldwide developed and emerging markets. Composed of annual and interim/quarterly data, detailed historical financial statement content, per-share data, and calculated ratios, FactSet Fundamentals provides you with the information you need for a global investment perspective.<p>This API is rate-limited to 10 requests per second and 10 concurrent requests per user.</p>   # noqa: E501

    The version of the OpenAPI document: 2.2.0
    Contact: api@factset.com
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401

from fds.sdk.FactSetFundamentals.model_utils import (  # noqa: F401
    ApiTypeError,
    ModelComposed,
    ModelNormal,
    ModelSimple,
    cached_property,
    change_keys_js_to_python,
    convert_js_args_to_python_args,
    date,
    datetime,
    file_type,
    none_type,
    validate_get_composed_info,
    OpenApiModel
)
from fds.sdk.FactSetFundamentals.exceptions import ApiAttributeError



class Metric(ModelNormal):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.

    Attributes:
      allowed_values (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          with a capitalized key describing the allowed value and an allowed
          value. These dicts store the allowed enum values.
      attribute_map (dict): The key is attribute name
          and the value is json key in definition.
      discriminator_value_class_map (dict): A dict to go from the discriminator
          variable value to the discriminator class name.
      validations (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          that stores validations for max_length, min_length, max_items,
          min_items, exclusive_maximum, inclusive_maximum, exclusive_minimum,
          inclusive_minimum, and regex.
      additional_properties_type (tuple): A tuple of classes accepted
          as additional properties values.
    """

    allowed_values = {
        ('sdf_package',): {
            'None': None,
            'BASIC': "BASIC",
            'ADVANCED': "ADVANCED",


        },
    }

    validations = {
    }

    @cached_property
    def additional_properties_type():
        """
        This must be a method because a model may have properties that are
        of type self, this must run after the class is loaded
        """
        return (bool, date, datetime, dict, float, int, list, str, none_type,)  # noqa: E501

    _nullable = False

    @cached_property
    def openapi_types():
        """
        This must be a method because a model may have properties that are
        of type self, this must run after the class is loaded

        Returns
            openapi_types (dict): The key is attribute name
                and the value is attribute type.
        """
        return {
            'metric': (str, none_type,),  # noqa: E501
            'name': (str, none_type,),  # noqa: E501
            'category': (str, none_type,),  # noqa: E501
            'subcategory': (str, none_type,),  # noqa: E501
            'oa_page_id': (str, none_type,),  # noqa: E501
            'oa_url': (str, none_type,),  # noqa: E501
            'factor': (int, none_type,),  # noqa: E501
            'sdf_package': (str, none_type,),  # noqa: E501
            'data_type': (str, none_type,),  # noqa: E501
        }

    @cached_property
    def discriminator():
        return None


    attribute_map = {
        'metric': 'metric',  # noqa: E501
        'name': 'name',  # noqa: E501
        'category': 'category',  # noqa: E501
        'subcategory': 'subcategory',  # noqa: E501
        'oa_page_id': 'oaPageId',  # noqa: E501
        'oa_url': 'oaUrl',  # noqa: E501
        'factor': 'factor',  # noqa: E501
        'sdf_package': 'sdfPackage',  # noqa: E501
        'data_type': 'dataType',  # noqa: E501
    }

    read_only_vars = {
    }

    _composed_schemas = {}

    @classmethod
    @convert_js_args_to_python_args
    def _from_openapi_data(cls, *args, **kwargs):  # noqa: E501
        """Metric - a model defined in OpenAPI

        Keyword Args:
            _check_type (bool): if True, values for parameters in openapi_types
                                will be type checked and a TypeError will be
                                raised if the wrong type is input.
                                Defaults to True
            _path_to_item (tuple/list): This is a list of keys or values to
                                drill down to the model in received_data
                                when deserializing a response
            _spec_property_naming (bool): True if the variable names in the input data
                                are serialized names, as specified in the OpenAPI document.
                                False if the variable names in the input data
                                are pythonic names, e.g. snake case (default)
            _configuration (Configuration): the instance to use when
                                deserializing a file_type parameter.
                                If passed, type conversion is attempted
                                If omitted no type conversion is done.
            _visited_composed_classes (tuple): This stores a tuple of
                                classes that we have traveled through so that
                                if we see that class again we will not use its
                                discriminator again.
                                When traveling through a discriminator, the
                                composed schema that is
                                is traveled through is added to this set.
                                For example if Animal has a discriminator
                                petType and we pass in "Dog", and the class Dog
                                allOf includes Animal, we move through Animal
                                once using the discriminator, and pick Dog.
                                Then in Dog, we will make an instance of the
                                Animal class but this time we won't travel
                                through its discriminator because we passed in
                                _visited_composed_classes = (Animal,)
            metric (str, none_type): Metric identifier to be used as `metrics` input in `/fundamentals/v#/fundamentals` endpoint.. [optional]  # noqa: E501
            name (str, none_type): Plain text name of the metric.. [optional]  # noqa: E501
            category (str, none_type): Primary Category of metric item, such as, INCOME_STATEMENT, BALANCE_SHEET, CASH_FLOW, or RATIOS.. [optional]  # noqa: E501
            subcategory (str, none_type): Sub-category of metric item, such as ASSETS, SUPPLEMENTAL, SHAREHOLDERS_EQUITY, VALUATION, PROFITABILITY, etc.. [optional]  # noqa: E501
            oa_page_id (str, none_type): The Online Assistant Page ID in D***** format, used to look up the definition and methodology of the requested item. Visit my.apps.factset.com/oa/pages/[D*****] for details. For example, https://my.apps.factset.com/oa/pages/D10585 will give you the definition for FF_SALES.. [optional]  # noqa: E501
            oa_url (str, none_type): The Online Assistant Page URL, is used to look up the definition and methodology of the requested item. For example, https://my.apps.factset.com/oa/pages/D10585 will give you the definition for FF_SALES.. [optional]  # noqa: E501
            factor (int, none_type): The factor for the metric (e.g. 1000 = thousands).. [optional]  # noqa: E501
            sdf_package (str, none_type): An indicator for which Standard Data Feed (SDF) package the item is available in - BASIC or ADVANCED. A null value represents items available only in API.. [optional]  # noqa: E501
            data_type (str, none_type): The data type for the metric. Make note, mixing data types within a single /fundamentals API is not supported. Each dataType is defined below -   * **date** - date format expressed in YYYY-MM-DD.   * **doubleArray** - A double is a FactSet data type, similar to a float or an integer. A double represents numeric data but provides a greater amount of decimal precision than the float data type. Double values have up to 15 digits of precision, while float values have up to 7 digits (integers have up to 10 digits).   * **float** - A float value is a real number (i.e., a number that can contain a fractional part/decimals). A float value has a precision of up to seven digits and accurately represents numbers whose absolute value is less than 16,277,216 (224). An example metric includes   * **floatArray** - Function will hold data for multiple periods, as well as for many companies (i.e., two-dimensional value). The FLOATARRAY function returns data using a vertical orientation (e.g., down a column). The difference between FLOAT and FLOATARRAY is that FLOAT can only go across a row (one-dimension; horizontal orientation; vertical length=1) whereas FLOATARRAY will return data both across a row and down a column (two-dimensions; vertical orientation). With FLOATARRAY, the number of data points across a row will correspond to the number of companies queried; the number of data points down a column will correspond to the length of the time series.   * **intArray** - An integer is a whole number or zero (i.e., integers do not include decimals). Integers can be positive or negative.   * **string** - A string value is an ASCII character. A string is a sequence of ASCII characters. String value and text value are synonymous. The function will hold data for multiple time periods, as well as for many companies (i.e., two-dimensional value). The STRING_ARRAY function returns data using a vertical orientation (e.g., down a column)   * **stringArray** - The difference between STRING and STRINGARRAY is that STRING can only go across a row (one-dimension; horizontal orientation; vertical length=1) whereas STRINGARRAY will return data both across a row and down a column (two-dimensions; vertical orientation). With STRINGARRAY, the number of data points across a row will correspond to the number of companies queried; the number of data points down a column will correspond to the length of the time series. . [optional]  # noqa: E501
        """

        _check_type = kwargs.pop('_check_type', True)
        _spec_property_naming = kwargs.pop('_spec_property_naming', False)
        _path_to_item = kwargs.pop('_path_to_item', ())
        _configuration = kwargs.pop('_configuration', None)
        _visited_composed_classes = kwargs.pop('_visited_composed_classes', ())

        self = super(OpenApiModel, cls).__new__(cls)

        if args:
            raise ApiTypeError(
                "Invalid positional arguments=%s passed to %s. Remove those invalid positional arguments." % (
                    args,
                    self.__class__.__name__,
                ),
                path_to_item=_path_to_item,
                valid_classes=(self.__class__,),
            )

        self._data_store = {}
        self._check_type = _check_type
        self._spec_property_naming = _spec_property_naming
        self._path_to_item = _path_to_item
        self._configuration = _configuration
        self._visited_composed_classes = _visited_composed_classes + (self.__class__,)

        for var_name, var_value in kwargs.items():
            if var_name not in self.attribute_map and \
                        self._configuration is not None and \
                        self._configuration.discard_unknown_keys and \
                        self.additional_properties_type is None:
                # discard variable.
                continue
            setattr(self, var_name, var_value)
        return self

    required_properties = set([
        '_data_store',
        '_check_type',
        '_spec_property_naming',
        '_path_to_item',
        '_configuration',
        '_visited_composed_classes',
    ])

    @convert_js_args_to_python_args
    def __init__(self, *args, **kwargs):  # noqa: E501
        """Metric - a model defined in OpenAPI

        Keyword Args:
            _check_type (bool): if True, values for parameters in openapi_types
                                will be type checked and a TypeError will be
                                raised if the wrong type is input.
                                Defaults to True
            _path_to_item (tuple/list): This is a list of keys or values to
                                drill down to the model in received_data
                                when deserializing a response
            _spec_property_naming (bool): True if the variable names in the input data
                                are serialized names, as specified in the OpenAPI document.
                                False if the variable names in the input data
                                are pythonic names, e.g. snake case (default)
            _configuration (Configuration): the instance to use when
                                deserializing a file_type parameter.
                                If passed, type conversion is attempted
                                If omitted no type conversion is done.
            _visited_composed_classes (tuple): This stores a tuple of
                                classes that we have traveled through so that
                                if we see that class again we will not use its
                                discriminator again.
                                When traveling through a discriminator, the
                                composed schema that is
                                is traveled through is added to this set.
                                For example if Animal has a discriminator
                                petType and we pass in "Dog", and the class Dog
                                allOf includes Animal, we move through Animal
                                once using the discriminator, and pick Dog.
                                Then in Dog, we will make an instance of the
                                Animal class but this time we won't travel
                                through its discriminator because we passed in
                                _visited_composed_classes = (Animal,)
            metric (str, none_type): Metric identifier to be used as `metrics` input in `/fundamentals/v#/fundamentals` endpoint.. [optional]  # noqa: E501
            name (str, none_type): Plain text name of the metric.. [optional]  # noqa: E501
            category (str, none_type): Primary Category of metric item, such as, INCOME_STATEMENT, BALANCE_SHEET, CASH_FLOW, or RATIOS.. [optional]  # noqa: E501
            subcategory (str, none_type): Sub-category of metric item, such as ASSETS, SUPPLEMENTAL, SHAREHOLDERS_EQUITY, VALUATION, PROFITABILITY, etc.. [optional]  # noqa: E501
            oa_page_id (str, none_type): The Online Assistant Page ID in D***** format, used to look up the definition and methodology of the requested item. Visit my.apps.factset.com/oa/pages/[D*****] for details. For example, https://my.apps.factset.com/oa/pages/D10585 will give you the definition for FF_SALES.. [optional]  # noqa: E501
            oa_url (str, none_type): The Online Assistant Page URL, is used to look up the definition and methodology of the requested item. For example, https://my.apps.factset.com/oa/pages/D10585 will give you the definition for FF_SALES.. [optional]  # noqa: E501
            factor (int, none_type): The factor for the metric (e.g. 1000 = thousands).. [optional]  # noqa: E501
            sdf_package (str, none_type): An indicator for which Standard Data Feed (SDF) package the item is available in - BASIC or ADVANCED. A null value represents items available only in API.. [optional]  # noqa: E501
            data_type (str, none_type): The data type for the metric. Make note, mixing data types within a single /fundamentals API is not supported. Each dataType is defined below -   * **date** - date format expressed in YYYY-MM-DD.   * **doubleArray** - A double is a FactSet data type, similar to a float or an integer. A double represents numeric data but provides a greater amount of decimal precision than the float data type. Double values have up to 15 digits of precision, while float values have up to 7 digits (integers have up to 10 digits).   * **float** - A float value is a real number (i.e., a number that can contain a fractional part/decimals). A float value has a precision of up to seven digits and accurately represents numbers whose absolute value is less than 16,277,216 (224). An example metric includes   * **floatArray** - Function will hold data for multiple periods, as well as for many companies (i.e., two-dimensional value). The FLOATARRAY function returns data using a vertical orientation (e.g., down a column). The difference between FLOAT and FLOATARRAY is that FLOAT can only go across a row (one-dimension; horizontal orientation; vertical length=1) whereas FLOATARRAY will return data both across a row and down a column (two-dimensions; vertical orientation). With FLOATARRAY, the number of data points across a row will correspond to the number of companies queried; the number of data points down a column will correspond to the length of the time series.   * **intArray** - An integer is a whole number or zero (i.e., integers do not include decimals). Integers can be positive or negative.   * **string** - A string value is an ASCII character. A string is a sequence of ASCII characters. String value and text value are synonymous. The function will hold data for multiple time periods, as well as for many companies (i.e., two-dimensional value). The STRING_ARRAY function returns data using a vertical orientation (e.g., down a column)   * **stringArray** - The difference between STRING and STRINGARRAY is that STRING can only go across a row (one-dimension; horizontal orientation; vertical length=1) whereas STRINGARRAY will return data both across a row and down a column (two-dimensions; vertical orientation). With STRINGARRAY, the number of data points across a row will correspond to the number of companies queried; the number of data points down a column will correspond to the length of the time series. . [optional]  # noqa: E501
        """

        _check_type = kwargs.pop('_check_type', True)
        _spec_property_naming = kwargs.pop('_spec_property_naming', False)
        _path_to_item = kwargs.pop('_path_to_item', ())
        _configuration = kwargs.pop('_configuration', None)
        _visited_composed_classes = kwargs.pop('_visited_composed_classes', ())

        if args:
            raise ApiTypeError(
                "Invalid positional arguments=%s passed to %s. Remove those invalid positional arguments." % (
                    args,
                    self.__class__.__name__,
                ),
                path_to_item=_path_to_item,
                valid_classes=(self.__class__,),
            )

        self._data_store = {}
        self._check_type = _check_type
        self._spec_property_naming = _spec_property_naming
        self._path_to_item = _path_to_item
        self._configuration = _configuration
        self._visited_composed_classes = _visited_composed_classes + (self.__class__,)

        for var_name, var_value in kwargs.items():
            if var_name not in self.attribute_map and \
                        self._configuration is not None and \
                        self._configuration.discard_unknown_keys and \
                        self.additional_properties_type is None:
                # discard variable.
                continue
            setattr(self, var_name, var_value)
            if var_name in self.read_only_vars:
                raise ApiAttributeError(f"`{var_name}` is a read-only attribute. Use `from_openapi_data` to instantiate "
                                     f"class with read only attributes.")
