class DisableIntrospectionMiddleware:
    def resolve(self, next, root, info, **args):
        if info.field_name in ["__schema", "__type", "__typename"]:
            raise Exception("Introspection is disabled")
        return next(root, info, **args)
