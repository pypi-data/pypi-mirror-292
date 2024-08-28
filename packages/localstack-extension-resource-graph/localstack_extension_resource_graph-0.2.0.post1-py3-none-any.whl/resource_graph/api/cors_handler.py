from localstack.aws.chain import Handler, HandlerChain
from localstack.http import Response
from rolo.gateway import RequestContext


class CorsLiberator(Handler):
    def __call__(self, chain: HandlerChain, context: RequestContext, response: Response) -> None:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"

        if context.request.method == "OPTIONS":
            # we want to return immediately here, but we do not want to omit our response chain for cors headers
            response.status_code = 204
            chain.stop()