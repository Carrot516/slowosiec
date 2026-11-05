
import "./AboutMe.css";

interface AboutMeProps {
  onClose: () => void;
}

// Wpisz tutaj swój adres przed publikacją aplikacji.
const CONTACT_EMAIL = "wojmarchewka@student.agh.edu.pl";

export default function AboutMe({ onClose }: AboutMeProps) {
  return (
    <section
      id="about-me"
      className="about-me"
      aria-labelledby="about-me-title"
    >
      <div className="about-me-header">
        <h2 id="about-me-title">O mnie</h2>

        <button
          type="button"
          className="about-me-close"
          onClick={onClose}
          aria-label="Zamknij sekcję O mnie"
        >
          ✕
        </button>
      </div>

      <p className="about-me-thanks">
        Bardzo dziękuję, że przyszliście na mój referat
        podczas konferencji Elements!
      </p>

      <p>
        Mam nadzieję, że prezentacja była dla Was ciekawa
        i że Słowosieć dostarczy Wam trochę dobrej zabawy.
      </p>

      <p>
        Jestem absolwentem studiów inżynierskich na kierunku
        <strong> informatyka stosowana</strong> oraz studiów
        licencjackich na kierunku <strong>matematyka</strong>.
        Obecnie jestem studentem pierwszego roku studiów
        magisterskich z matematyki na
        <strong> Akademii Górniczo-Hutniczej w Krakowie</strong>.
      </p>

      <p>
        Interesuję się matematyką, programowaniem i sztuczną
        inteligencją. Słowosieć to mój niewielki projekt
        łączący te dziedziny, przygotowany z myślą
        o konferencji.
      </p>

      <p>
        Jeśli macie pytania dotyczące projektu lub chcecie
        się skontaktować, śmiało napiszcie!
      </p>

      <div className="about-me-contact">
        <span>Kontakt</span>

        {CONTACT_EMAIL ? (
          <a href={`mailto:${CONTACT_EMAIL}`}>
            {CONTACT_EMAIL}
          </a>
        ) : (
          <span className="about-me-placeholder">
            Adres e-mail zostanie uzupełniony.
          </span>
        )}
      </div>
    </section>
  );
}
