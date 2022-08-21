"""Module with custom providers for ``faker``."""
import factory
import faker.config
import faker.providers as providers


class Provider(providers.BaseProvider):
    """Custom provider class for Faker."""

    def sem_version(self, elements: int = 3) -> str:
        """Generated SemVer version.

        Args:
            elements: Number of elements in the version, separated by dot.

        Returns:
            SemVer version.
        """
        return ".".join(tuple(str(self.random_digit()) for _ in range(elements)))


faker.config.PROVIDERS.append("tests.custom_fakes")
factory.Faker.add_provider(Provider)
