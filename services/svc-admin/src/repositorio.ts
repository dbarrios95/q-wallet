// Acceso de svc-admin: Cognito (listar, deshabilitar, cerrar sesiones, ver grupos) y auditoria (Query/Put).
import {
  AdminDisableUserCommand,
  AdminListGroupsForUserCommand,
  AdminUserGlobalSignOutCommand,
  CognitoIdentityProviderClient,
  ListUsersCommand,
  UserNotFoundException,
} from "@aws-sdk/client-cognito-identity-provider";
import { QueryCommand, type DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";

export interface UsuarioCognito {
  id: string;
  correo: string | null;
  habilitado: boolean;
  estado: string;
  creado: string | null;
}

export interface RepositorioAdmin {
  listarUsuarios(limite: number, token?: string): Promise<{ usuarios: UsuarioCognito[]; siguiente?: string }>;
  gruposDe(id: string): Promise<string[] | null>;
  bloquear(id: string): Promise<void>;
  auditoria(dia: string, limite: number, desde?: Record<string, string>): Promise<{ items: Record<string, unknown>[]; siguiente?: Record<string, unknown> }>;
}

export function repositorioAws(cognito: CognitoIdentityProviderClient, userPoolId: string, c: DynamoDBDocumentClient, tablaAuditoria: string): RepositorioAdmin {
  return {
    async listarUsuarios(limite, token) {
      const r = await cognito.send(new ListUsersCommand({ UserPoolId: userPoolId, Limit: limite, PaginationToken: token, AttributesToGet: ["email"] }));
      return {
        usuarios: (r.Users ?? []).map((u) => ({
          id: u.Username ?? "",
          correo: u.Attributes?.find((a) => a.Name === "email")?.Value ?? null,
          habilitado: u.Enabled ?? false,
          estado: u.UserStatus ?? "desconocido",
          creado: u.UserCreateDate?.toISOString() ?? null,
        })),
        ...(r.PaginationToken ? { siguiente: r.PaginationToken } : {}),
      };
    },
    async gruposDe(id) {
      try {
        const r = await cognito.send(new AdminListGroupsForUserCommand({ UserPoolId: userPoolId, Username: id, Limit: 10 }));
        return (r.Groups ?? []).map((g) => g.GroupName ?? "");
      } catch (e) {
        if (e instanceof UserNotFoundException) return null;
        throw e;
      }
    },
    async bloquear(id) {
      await cognito.send(new AdminDisableUserCommand({ UserPoolId: userPoolId, Username: id }));
      // Cierra las sesiones abiertas: los refresh token dejan de servir.
      await cognito.send(new AdminUserGlobalSignOutCommand({ UserPoolId: userPoolId, Username: id }));
    },
    async auditoria(dia, limite, desde) {
      const r = await c.send(
        new QueryCommand({
          TableName: tablaAuditoria,
          KeyConditionExpression: "dia = :d",
          ExpressionAttributeValues: { ":d": dia },
          ScanIndexForward: false,
          Limit: limite,
          ExclusiveStartKey: desde,
        }),
      );
      return { items: (r.Items ?? []) as Record<string, unknown>[], siguiente: r.LastEvaluatedKey };
    },
  };
}
