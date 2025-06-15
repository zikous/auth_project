import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
import graphql_jwt
from graphql_jwt.decorators import login_required
from graphql_jwt.refresh_token.shortcuts import create_refresh_token
from graphql_jwt.shortcuts import get_token

User = get_user_model()


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "email", "date_joined", "is_active")


class CreateUserMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, email, password):
        if User.objects.filter(email=email).exists():
            return CreateUserMutation(
                success=False, message="User with this email already exists"
            )

        user = User.objects.create_user(
            email=email,
            password=password,
        )

        return CreateUserMutation(
            user=user, success=True, message="User created successfully"
        )


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)

    @login_required
    def resolve_me(self, info):
        return info.context.user


class Mutation(graphene.ObjectType):
    register = CreateUserMutation.Field()

    # JWT mutations
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()
