"""
    Open:Risk API

    Service to calculate parametric linear risk statistics and generate risk model asset identifier mappings.  # noqa: E501

    The version of the OpenAPI document: 1.26.0
    Contact: api@factset.com
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401

from fds.sdk.OpenRisk.model_utils import (  # noqa: F401
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
from fds.sdk.OpenRisk.exceptions import ApiAttributeError



class SupportedStatDetailsSecurityGroupMethod(ModelNormal):
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
        ('name',): {
            'STATSPECIFIC': "StatSpecific",
            'SUM': "Sum",
            'WEIGHTEDAVERAGE': "WeightedAverage",
            'WEIGHTEDNORMALIZEDAVERAGE': "WeightedNormalizedAverage",
            'WEIGHTEDNORMALIZEDAVERAGEFILL': "WeightedNormalizedAverageFill",


        },
        ('weights',): {
            'PORTFOLIOWEIGHTS': "PortfolioWeights",
            'BENCHMARKWEIGHTS': "BenchmarkWeights",
            'ACTIVEWEIGHTS': "ActiveWeights",
            'MARKETWEIGHTS': "MarketWeights",


        },
        ('weighting',): {
            'ABSOLUTEVALUE': "AbsoluteValue",
            'ACTUALVALUE': "ActualValue",


        },
    }

    validations = {
        ('name',): {
            'min_length': 1,
        },
        ('weights',): {
            'min_length': 1,
        },
        ('weighting',): {
            'min_length': 1,
        },
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
            'name': (str,),  # noqa: E501
            'sqrt': (bool,),  # noqa: E501
            'weights': (str,),  # noqa: E501
            'weighting': (str,),  # noqa: E501
        }

    @cached_property
    def discriminator():
        return None


    attribute_map = {
        'name': 'name',  # noqa: E501
        'sqrt': 'sqrt',  # noqa: E501
        'weights': 'weights',  # noqa: E501
        'weighting': 'weighting',  # noqa: E501
    }

    read_only_vars = {
    }

    _composed_schemas = {}

    @classmethod
    @convert_js_args_to_python_args
    def _from_openapi_data(cls, name, sqrt, *args, **kwargs):  # noqa: E501
        """SupportedStatDetailsSecurityGroupMethod - a model defined in OpenAPI

        Args:
            name (str): Indicates the algorithm used to compute each security group's value from the  risk statistic values of its member securities. 'Sum' takes the sum of all members' values. The weighted average methods indicate 'weights' and 'weighting'. 'WeightedAverage' weights each group's members' statistic values and takes their average. 'WeightedNormalizedAverage' normalizes the corresponding weights belonging within each group, weights each group's members' statistic values, then takes the average. 'WeightedNormalizedAverageFill' normalizes the corresponding weights belonging within each group or applies equal weighting for groups with zero net weight, weights each group's members' statistic values, then takes the average. 'StatSpecific' indicates unique calculations for the supported security group levels (inquire for more information).
            sqrt (bool): Indicates whether the square root of each security group's value is taken (or not) as the final step of the calculation after the indicated algorithm to produce the result.

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
            weights (str): Indicates the weights stat used to weight the security groups, applicable to weighted average group methods only.. [optional]  # noqa: E501
            weighting (str): Indicates the weighting method used when allocating a net-weight position of risk statistics to multiple lots. This is relevant when a portfolio contains multiple lots with different signs such as long/short. For example, the case where a net-weight position is a positive risk contributor and a portfolio contains long and short positions. If this is 'AbsoluteValue', both long/short positions will have positive risk contribution, while 'ActualValue' assigns positive risk contribution to a long position and negative risk contribution to a short position. Applicable to weighted average group methods only.. [optional]  # noqa: E501
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

        self.name = name
        self.sqrt = sqrt
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
    def __init__(self, name, sqrt, *args, **kwargs):  # noqa: E501
        """SupportedStatDetailsSecurityGroupMethod - a model defined in OpenAPI

        Args:
            name (str): Indicates the algorithm used to compute each security group's value from the  risk statistic values of its member securities. 'Sum' takes the sum of all members' values. The weighted average methods indicate 'weights' and 'weighting'. 'WeightedAverage' weights each group's members' statistic values and takes their average. 'WeightedNormalizedAverage' normalizes the corresponding weights belonging within each group, weights each group's members' statistic values, then takes the average. 'WeightedNormalizedAverageFill' normalizes the corresponding weights belonging within each group or applies equal weighting for groups with zero net weight, weights each group's members' statistic values, then takes the average. 'StatSpecific' indicates unique calculations for the supported security group levels (inquire for more information).
            sqrt (bool): Indicates whether the square root of each security group's value is taken (or not) as the final step of the calculation after the indicated algorithm to produce the result.

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
            weights (str): Indicates the weights stat used to weight the security groups, applicable to weighted average group methods only.. [optional]  # noqa: E501
            weighting (str): Indicates the weighting method used when allocating a net-weight position of risk statistics to multiple lots. This is relevant when a portfolio contains multiple lots with different signs such as long/short. For example, the case where a net-weight position is a positive risk contributor and a portfolio contains long and short positions. If this is 'AbsoluteValue', both long/short positions will have positive risk contribution, while 'ActualValue' assigns positive risk contribution to a long position and negative risk contribution to a short position. Applicable to weighted average group methods only.. [optional]  # noqa: E501
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

        self.name = name
        self.sqrt = sqrt
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
