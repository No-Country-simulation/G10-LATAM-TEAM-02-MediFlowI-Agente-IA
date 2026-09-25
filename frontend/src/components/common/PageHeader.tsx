import type { ReactNode } from 'react'

interface PageHeaderProps {
  title: string
  description: string
  eyebrow?: string
  icon?: ReactNode
  actions?: ReactNode
}

const PageHeader = ({ title, description, eyebrow, icon, actions }: PageHeaderProps) => (
  <header className="clinical-page-header">
    <div className="clinical-page-header__identity">
      {icon && <div className="clinical-page-header__icon" aria-hidden="true">{icon}</div>}
      <div>
        {eyebrow && <span className="clinical-page-header__eyebrow">{eyebrow}</span>}
        <h1 className="clinical-page-header__title">{title}</h1>
        <p className="clinical-page-header__description">{description}</p>
      </div>
    </div>
    {actions && <div className="clinical-page-header__actions">{actions}</div>}
  </header>
)

export default PageHeader
