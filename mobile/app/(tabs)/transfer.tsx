import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Modal,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { useRouter } from "expo-router";
import { usePreventScreenCapture } from "expo-screen-capture";
import { z } from "zod";
import {
  Send,
  Phone,
  CheckCircle2,
  Lock,
  ArrowRight,
  ShieldCheck,
  X,
} from "lucide-react-native";
import { useTheme } from "../../src/theme";
import { Header, Input, Button, Card } from "../../src/components";
import { formatGTQ } from "../../src/components/BalanceCard";
import { mockAccount, mockBeneficiaries, Beneficiary } from "../../src/mocks";

// Esquema Zod estricto para validar la transferencia
const transferFormSchema = z
  .object({
    phone: z
      .string()
      .regex(
        /^[2-5][0-9]{7}$/,
        "El número debe ser de 8 dígitos válido de Guatemala"
      ),
    amountCents: z
      .number()
      .int("El monto debe ser un entero en centavos")
      .positive("El monto debe ser mayor a cero")
      .max(mockAccount.balanceCents, "El monto supera el saldo disponible"),
    note: z.string().max(60, "La nota no puede superar 60 caracteres"),
  })
  .strict();

export default function TransferScreen() {
  const router = useRouter();
  const { colors, palette, isDark } = useTheme();

  // FLAG_SECURE: previene captura de pantalla durante transferencias y PIN (MASVS-STORAGE)
  usePreventScreenCapture();

  const [phone, setPhone] = useState("");
  const [amountStr, setAmountStr] = useState("");
  const [note, setNote] = useState("");
  const [selectedBeneficiary, setSelectedBeneficiary] = useState<Beneficiary | null>(null);
  const [formErrors, setFormErrors] = useState<{ phone?: string; amount?: string }>({});

  // PIN modal & confirmación
  const [showPinModal, setShowPinModal] = useState(false);
  const [pin, setPin] = useState("");
  const [pinError, setPinError] = useState<string | undefined>();
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSelectBeneficiary = (b: Beneficiary) => {
    setSelectedBeneficiary(b);
    setPhone(b.phone);
    setFormErrors((prev) => ({ ...prev, phone: undefined }));
  };

  const handleContinue = () => {
    setFormErrors({});

    const amountFloat = parseFloat(amountStr.replace(",", "."));
    const amountCents = isNaN(amountFloat) ? 0 : Math.round(amountFloat * 100);

    const validation = transferFormSchema.safeParse({
      phone: phone.trim(),
      amountCents,
      note: note.trim(),
    });

    if (!validation.success) {
      const errors: { phone?: string; amount?: string } = {};
      validation.error.issues.forEach((issue) => {
        if (issue.path[0] === "phone") errors.phone = issue.message;
        if (issue.path[0] === "amountCents") errors.amount = issue.message;
      });
      setFormErrors(errors);
      return;
    }

    setPin("");
    setPinError(undefined);
    setShowPinModal(true);
  };

  // TODO(CTRL-02): Verificación de hash scrypt del PIN en backend y política de bloqueo de 15 min tras 5 intentos
  // TODO(CTRL-06): Envío de Idempotency-Key en cabecera HTTP hacia POST /transfers
  const handleConfirmTransfer = () => {
    if (pin.length !== 6) {
      setPinError("Debes ingresar tu PIN de 6 dígitos");
      return;
    }

    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setShowPinModal(false);
      setIsSuccess(true);
    }, 1000);
  };

  const handleReset = () => {
    setIsSuccess(false);
    setPhone("");
    setAmountStr("");
    setNote("");
    setSelectedBeneficiary(null);
  };

  if (isSuccess) {
    const amountFloat = parseFloat(amountStr.replace(",", "."));
    const amountCents = Math.round(amountFloat * 100);

    return (
      <View style={[styles.container, { backgroundColor: colors.background }]}>
        <Header title="Comprobante" />
        <View style={styles.successContent}>
          <View style={[styles.successIconCircle, { backgroundColor: "rgba(0, 168, 107, 0.15)" }]}>
            <CheckCircle2 size={64} color={palette.accent} />
          </View>

          <Text style={[styles.successTitle, { color: colors.text }]}>
            ¡Transferencia Exitosa!
          </Text>
          <Text style={[styles.successSubtitle, { color: colors.textMuted }]}>
            El dinero ha sido enviado inmediatamente
          </Text>

          <Card style={styles.receiptCard}>
            <View style={styles.receiptRow}>
              <Text style={[styles.receiptLabel, { color: colors.textMuted }]}>Monto enviado</Text>
              <Text style={[styles.receiptAmount, { color: palette.accent }]}>
                {formatGTQ(amountCents)}
              </Text>
            </View>

            <View style={styles.divider} />

            <View style={styles.receiptRow}>
              <Text style={[styles.receiptLabel, { color: colors.textMuted }]}>Destinatario</Text>
              <Text style={[styles.receiptValue, { color: colors.text }]}>
                {selectedBeneficiary ? selectedBeneficiary.name : `Tel: +502 ${phone}`}
              </Text>
            </View>

            <View style={styles.receiptRow}>
              <Text style={[styles.receiptLabel, { color: colors.textMuted }]}>Número de teléfono</Text>
              <Text style={[styles.receiptValue, { color: colors.text }]}>
                +502 {phone}
              </Text>
            </View>

            <View style={styles.receiptRow}>
              <Text style={[styles.receiptLabel, { color: colors.textMuted }]}>Referencia</Text>
              <Text style={[styles.receiptValue, { color: colors.text }]}>
                QW-{Math.floor(100000 + Math.random() * 900000)}
              </Text>
            </View>

            {note.trim() ? (
              <View style={styles.receiptRow}>
                <Text style={[styles.receiptLabel, { color: colors.textMuted }]}>Concepto</Text>
                <Text style={[styles.receiptValue, { color: colors.text }]}>
                  {note}
                </Text>
              </View>
            ) : null}
          </Card>

          <View style={styles.successActions}>
            <Button
              title="Nueva transferencia"
              onPress={handleReset}
              variant="accent"
              size="lg"
            />
            <View style={{ height: 10 }} />
            <Button
              title="Volver al inicio"
              onPress={() => router.replace("/(tabs)/home")}
              variant="secondary"
              size="md"
            />
          </View>
        </View>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      style={[styles.container, { backgroundColor: colors.background }]}
    >
      <Header title="Transferir Quetzales" />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* Beneficiarios Frecuentes */}
        <Text style={[styles.sectionTitle, { color: colors.text }]}>
          Beneficiarios Frecuentes
        </Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.beneficiariesList}
        >
          {mockBeneficiaries.map((b) => {
            const isSelected = selectedBeneficiary?.id === b.id;
            return (
              <TouchableOpacity
                key={b.id}
                onPress={() => handleSelectBeneficiary(b)}
                style={[
                  styles.beneficiaryChip,
                  {
                    backgroundColor: isSelected
                      ? palette.primary
                      : colors.card,
                    borderColor: isSelected ? palette.accent : colors.cardBorder,
                  },
                ]}
                activeOpacity={0.7}
              >
                <View
                  style={[
                    styles.avatarBadge,
                    { backgroundColor: b.avatarColor },
                  ]}
                >
                  <Text style={styles.avatarInitials}>
                    {b.name.slice(0, 2).toUpperCase()}
                  </Text>
                </View>
                <Text
                  style={[
                    styles.beneficiaryName,
                    { color: isSelected ? "#FFFFFF" : colors.text },
                  ]}
                  numberOfLines={1}
                >
                  {b.name}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>

        {/* Transfer Form Card */}
        <Card style={styles.formCard}>
          <Input
            label="Número de Teléfono Destino"
            placeholder="ej. 55551234"
            keyboardType="number-pad"
            maxLength={8}
            value={phone}
            onChangeText={(txt) => {
              setPhone(txt);
              if (selectedBeneficiary && txt !== selectedBeneficiary.phone) {
                setSelectedBeneficiary(null);
              }
            }}
            leftIcon={<Phone size={20} color={colors.textMuted} />}
            error={formErrors.phone}
            helper="8 dígitos numéricos de Guatemala"
          />

          <Input
            label="Monto en Quetzales (GTQ)"
            placeholder="0.00"
            keyboardType="decimal-pad"
            value={amountStr}
            onChangeText={setAmountStr}
            error={formErrors.amount}
            helper={`Disponible: ${formatGTQ(mockAccount.balanceCents)}`}
          />

          <Input
            label="Concepto / Mensaje (opcional)"
            placeholder="ej. Pago almuerzo"
            value={note}
            onChangeText={setNote}
            maxLength={60}
          />

          <View style={{ height: 12 }} />

          <Button
            title="Continuar a confirmación"
            onPress={handleContinue}
            variant="accent"
            size="lg"
            icon={<ArrowRight size={20} color="#FFFFFF" />}
            iconPosition="right"
          />
        </Card>

        {/* Security Info Box */}
        <View style={styles.securityBox}>
          <ShieldCheck size={18} color={palette.accent} />
          <Text style={[styles.securityText, { color: colors.textMuted }]}>
            Protegido con PIN de 6 dígitos y comprobación de saldo en tiempo real.
          </Text>
        </View>
      </ScrollView>

      {/* Modal de confirmación y autorización con PIN */}
      <Modal
        visible={showPinModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowPinModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View
            style={[
              styles.modalContainer,
              { backgroundColor: colors.surface },
            ]}
          >
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, { color: colors.text }]}>
                Autorizar Transferencia
              </Text>
              <TouchableOpacity
                onPress={() => setShowPinModal(false)}
                style={styles.closeButton}
              >
                <X size={20} color={colors.textMuted} />
              </TouchableOpacity>
            </View>

            <View style={styles.modalSummary}>
              <Text style={[styles.summaryAmount, { color: palette.accent }]}>
                {formatGTQ(
                  Math.round(parseFloat(amountStr.replace(",", ".") || "0") * 100)
                )}
              </Text>
              <Text style={[styles.summaryDest, { color: colors.textMuted }]}>
                Hacia: +502 {phone}
                {selectedBeneficiary ? ` (${selectedBeneficiary.name})` : ""}
              </Text>
            </View>

            <View style={styles.modalPinSection}>
              <Text style={[styles.pinLabel, { color: colors.text }]}>
                Ingresa tu PIN de 6 dígitos para autorizar
              </Text>
              <Input
                variant="pin"
                pinLength={6}
                value={pin}
                onChangeText={(t) => {
                  setPin(t);
                  if (t.length === 6) setPinError(undefined);
                }}
                error={pinError}
                autoFocus
              />
            </View>

            <Button
              title="Confirmar y Transferir"
              onPress={handleConfirmTransfer}
              variant="accent"
              size="lg"
              loading={isProcessing}
            />
          </View>
        </View>
      </Modal>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 32,
  },
  sectionTitle: {
    fontSize: 15,
    fontFamily: "Inter_600SemiBold",
    marginTop: 8,
    marginBottom: 12,
  },
  beneficiariesList: {
    gap: 10,
    paddingBottom: 8,
    marginBottom: 16,
  },
  beneficiaryChip: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 24,
    borderWidth: 1.5,
    gap: 8,
  },
  avatarBadge: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
  },
  avatarInitials: {
    color: "#FFFFFF",
    fontSize: 11,
    fontFamily: "Inter_700Bold",
  },
  beneficiaryName: {
    fontSize: 13,
    fontFamily: "Inter_600SemiBold",
    maxWidth: 120,
  },
  formCard: {
    marginTop: 4,
    marginBottom: 16,
  },
  securityBox: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingHorizontal: 8,
  },
  securityText: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
    flex: 1,
    lineHeight: 18,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    justifyContent: "flex-end",
  },
  modalContainer: {
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    paddingBottom: 36,
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 18,
    fontFamily: "Inter_700Bold",
  },
  closeButton: {
    padding: 4,
  },
  modalSummary: {
    alignItems: "center",
    marginVertical: 12,
  },
  summaryAmount: {
    fontSize: 28,
    fontFamily: "Inter_700Bold",
    marginBottom: 4,
  },
  summaryDest: {
    fontSize: 14,
    fontFamily: "Inter_400Regular",
  },
  modalPinSection: {
    marginVertical: 18,
    alignItems: "center",
  },
  pinLabel: {
    fontSize: 14,
    fontFamily: "Inter_500Medium",
    marginBottom: 8,
  },
  successContent: {
    flex: 1,
    alignItems: "center",
    paddingHorizontal: 24,
    paddingTop: 24,
    paddingBottom: 32,
    justifyContent: "space-between",
  },
  successIconCircle: {
    width: 100,
    height: 100,
    borderRadius: 50,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 16,
  },
  successTitle: {
    fontSize: 24,
    fontFamily: "Inter_700Bold",
    marginBottom: 6,
  },
  successSubtitle: {
    fontSize: 14,
    fontFamily: "Inter_400Regular",
    textAlign: "center",
  },
  receiptCard: {
    width: "100%",
    marginVertical: 20,
    gap: 12,
  },
  receiptRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  receiptLabel: {
    fontSize: 13,
    fontFamily: "Inter_400Regular",
  },
  receiptValue: {
    fontSize: 13,
    fontFamily: "Inter_600SemiBold",
  },
  receiptAmount: {
    fontSize: 18,
    fontFamily: "Inter_700Bold",
  },
  divider: {
    height: 1,
    backgroundColor: "rgba(148, 163, 184, 0.2)",
    marginVertical: 4,
  },
  successActions: {
    width: "100%",
  },
});
