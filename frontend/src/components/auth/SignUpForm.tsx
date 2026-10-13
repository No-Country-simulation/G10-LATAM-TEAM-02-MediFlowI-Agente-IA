import { useState, type FormEvent, type JSX } from 'react';
import { signupUser } from '../../api/auth.api';
import type { User } from '../../api/auth.api';
import { Button, Input, Alert } from "../common";
import FooterDivider from '../login/FooterDivider';

interface SignUpFormProps {
  onSuccess?: (user: User, password?: string, correo?: string) => void;
  onNavigateToLogin?: () => void;
}

export function SignUpForm({ onSuccess, onNavigateToLogin }: SignUpFormProps): JSX.Element {
  const [formData, setFormData] = useState({
    nombres: '',
    apellidos: '',
    documento_identidad: '',
    telefono: '',
    correo: '',
    password: '',
    confirmPassword: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successAlert, setSuccessAlert] = useState(false);
  const [serverErrorAlert, setServerErrorAlert] = useState(false);

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.nombres.trim()) {
      newErrors.nombres = 'Por favor ingrese su nombre.';
    }
    if (!formData.apellidos.trim()) {
      newErrors.apellidos = 'Por favor ingrese sus apellidos.';
    }

    const docRegex = /^\d{8}$/;
    if (!formData.documento_identidad.trim() || !docRegex.test(formData.documento_identidad.trim())) {
      newErrors.documento_identidad = 'El número de identificación debe tener 8 dígitos.';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.correo.trim() || !emailRegex.test(formData.correo.trim())) {
      newErrors.correo = 'Por favor, introduzca una dirección de correo electrónico válida';
    }
    const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$/;
    if (!passwordRegex.test(formData.password)) {
      newErrors.password =
        'La contraseña debe tener al menos 8 caracteres, 1 mayúscula, 1 número y 1 carácter especial.';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Las contraseñas no coinciden.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSuccessAlert(false);
    setServerErrorAlert(false);

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const user = await signupUser({
        documento_identidad: formData.documento_identidad.trim(),
        nombres: formData.nombres.trim(),
        apellidos: formData.apellidos.trim(),
        telefono: formData.telefono.trim() || undefined,
        correo: formData.correo.trim(),
        password: formData.password,
      });

      setSuccessAlert(true);
      if (onSuccess) {
        onSuccess(user, formData.password, formData.correo.trim());
      }
    } catch (err: any) {
      const msg = err.message || '';
      if (msg.includes('documento de identidad')) {
        setErrors((prev) => ({ ...prev, documento_identidad: msg }));
      } else if (msg.includes('correo electrónico')) {
        setErrors((prev) => ({ ...prev, correo: msg }));
      } else {
        setServerErrorAlert(true);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const isFormFilled =
    formData.nombres.trim() !== '' &&
    formData.apellidos.trim() !== '' &&
    formData.documento_identidad.trim() !== '' &&
    formData.correo.trim() !== '' &&
    formData.password !== '' &&
    formData.confirmPassword !== '';

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="flex flex-col w-full max-w-[540px] items-center gap-3.5 mt-0.5"
    >
      <div className="flex flex-col items-center gap-1 w-full text-center">
        <h1
          id="signup-heading"
          className="font-bold text-[#1f2041] text-2xl sm:text-[28px] tracking-tight"
          style={{ fontFamily: "'Quicksand', sans-serif" }}
        >
          Crea tu cuenta
        </h1>
        <p
          className="font-normal text-xs sm:text-sm text-[rgba(31,32,65,0.5)] max-w-[440px] leading-relaxed"
          style={{ fontFamily: "'Montserrat', sans-serif" }}
        >
          Por favor ingrese los siguientes datos para proceder con su solicitud de acceso
        </p>
      </div>

      {/* Alerta de Éxito */}
      {successAlert && (
        <Alert
          type="success"
          title="¡Registro exitoso!"
          message="Tu solicitud de acceso ha sido enviada al administrador del sistema, por favor, espera a que sea confirmada para comenzar."
          onClose={() => setSuccessAlert(false)}
        />
      )}

      {/* Alerta de Error del Servidor */}
      {serverErrorAlert && (
        <Alert
          type="error"
          title="Error Interno del Servidor"
          message="Ocurrió un error inesperado al procesar la solicitud en el servidor."
          onClose={() => setServerErrorAlert(false)}
        />
      )}

      <div className="flex flex-col gap-2.5 w-full">
        {/* Fila 1: NOMBRE(S) y APELLIDOS */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-2.5 w-full">
          <Input
            type="text"
            name="nombres"
            value={formData.nombres}
            onChange={handleChange}
            placeholder="Ej. María Fernanda"
            label="NOMBRE(S)"
            error={errors.nombres}
            disabled={isSubmitting}
          />
          <Input
            type="text"
            name="apellidos"
            value={formData.apellidos}
            onChange={handleChange}
            placeholder="Ej. Castañeda Hernández"
            label="APELLIDOS"
            error={errors.apellidos}
            disabled={isSubmitting}
          />
        </div>

        {/* Fila 2: NÚMERO DE IDENTIFICACIÓN y NÚMERO TELEFÓNICO */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-2.5 w-full">
          <Input
            type="text"
            name="documento_identidad"
            value={formData.documento_identidad}
            onChange={handleChange}
            placeholder="00000000"
            label="NÚMERO DE IDENTIFICACIÓN"
            error={errors.documento_identidad}
            disabled={isSubmitting}
            inputMode="numeric"
            maxLength={8}
          />
          <Input
            type="tel"
            name="telefono"
            value={formData.telefono}
            onChange={handleChange}
            placeholder="Ej. (+52) 555-152-3056"
            label="NÚMERO TELEFÓNICO"
            error={errors.telefono}
            disabled={isSubmitting}
          />
        </div>

        {/* Fila 3: CORREO */}
        <Input
          type="email"
          name="correo"
          value={formData.correo}
          onChange={handleChange}
          placeholder="email@example.com"
          label="CORREO"
          error={errors.correo}
          disabled={isSubmitting}
        />

        {/* Fila 4: CONTRASEÑA */}
        <Input
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="••••••••••••"
          label="CONTRASEÑA"
          error={errors.password}
          disabled={isSubmitting}
        />

        {/* Fila 5: CONFIRMA TU CONTRASEÑA */}
        <Input
          type="password"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleChange}
          placeholder="••••••••••••"
          label="CONFIRMA TU CONTRASEÑA"
          error={errors.confirmPassword}
          disabled={isSubmitting}
        />
      </div>

      <div className="flex flex-col gap-3 w-full mt-2">
        <Button
          type="submit"
          text="Enviar solicitud"
          loading={isSubmitting}
          disabled={isSubmitting || !isFormFilled}
        />

        {/* Separador OR */}
        <FooterDivider
          lightText="¿Ya tiene una cuenta?"
          boldText="Inicie sesión"
          onNavigate={onNavigateToLogin}
        />
      </div >
    </form>
  );
}
