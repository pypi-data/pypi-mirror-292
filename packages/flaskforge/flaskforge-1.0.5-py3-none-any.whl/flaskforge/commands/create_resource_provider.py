from flaskforge.writers.writer_factory import WriterFactory

from .base_cli_provider import AbstractProvider


class CreateResourceProvider(AbstractProvider):
    def handler(self, args: object):

        name = args.name

        if args.use_single and (args.param is None or args.type is None):
            raise AttributeError(
                "Param and Type is required when use-single is flagged"
            )

        writers = ["resource", "route", "swagger"]

        for w in writers:
            writer = WriterFactory(w, args)
            writer.set_writable(name)
            writer.write_source()
