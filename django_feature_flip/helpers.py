import random
import zlib

from django_feature_flip.models import Group, Feature


class FeatureFlip:
    class FeatureFlipError(Exception):
        def __init__(self, message):
            self.message = message

    class __FeatureFlip:
        def __init__(self):
            self.groups = {}

        def __str__(self):
            return repr(self)

    instance = None

    def __init__(self):
        if not FeatureFlip.instance:
            FeatureFlip.instance = FeatureFlip.__FeatureFlip()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def enabled(self, feature_name, actor=None):
        feature = get_feature_or_raise_error(feature_name)

        if feature.totally_enabled or in_time_percentage(feature):
            return True
        elif actor:
            return (
                self.feature_enabled_for_a_group_of_actor(feature, actor) or
                self.feature_enabled_for_actor(feature, actor)
            )
        else:
            return False

    def register(self, group_name, func):
        Group.objects.get_or_create(name=group_name)

        self.groups[group_name] = func

    def activate_group(self, feature_name, group_name):
        feature = get_feature_or_raise_error(feature_name)

        get_group_or_raise_error(group_name).features.add(feature)

    def feature_enabled_for_a_group_of_actor(self, feature, actor):
        groups_names = [group.name for group in feature.group_set.all()]
        return any(self.groups[group_name](actor) for group_name in groups_names)

    def feature_enabled_for_actor(self, feature, actor):
        if (actors_percentage := feature.actors_percentage):
            flip_id = actor.flip_id()
            generated_id = str.encode(f"#{feature.name}#{flip_id}")
            scaling_factor = 1_000
            # this is to support up to 3 decimal places in percentages
            return zlib.crc32(generated_id) % (100 * scaling_factor) < actors_percentage * scaling_factor
        else:
            return False

    def enable_time_percentage(self, feature_name, time_percentage):
        feature = Feature.objects.get(name=feature_name)
        feature.time_percentage = time_percentage
        feature.clean_fields()

        return feature.save()

    def enable_actors_percentage(self, feature_name, actors_percentage):
        feature = get_feature_or_raise_error(feature_name)
        feature.actors_percentage = actors_percentage
        feature.clean_fields()

        return feature.save()


def get_feature_or_raise_error(feature_name):
    try:
        return Feature.objects.get(name=feature_name)
    except Feature.DoesNotExist:
        raise FeatureFlip.FeatureFlipError(f'Feature {feature_name} does not exist')


def get_group_or_raise_error(group_name):
    try:
        return Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        raise FeatureFlip.FeatureFlipError(f'Group {group_name} does not exist')


def in_time_percentage(feature):
    return feature.time_percentage > 0 and feature.time_percentage > random.randint(0, 100)
