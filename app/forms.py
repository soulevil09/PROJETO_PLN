from django import forms

class ChatForm(forms.Form):
    # O campo principal para a entrada do usuário (prompt)
    prompt = forms.CharField(
        label='Sua pergunta ou instrução para o modelo:',
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Ex: "Explique o que é Processamento de Linguagem Natural em uma frase."',
            'class': 'form-control' # Classe do Bootstrap para estilo
        })
    )

    # Parâmetros avançados (max_new_tokens)
    max_new_tokens = forms.IntegerField(
        label='Max. de Tokens na Resposta',
        initial=150,
        min_value=1,
        max_value=2048,
        required=False, # Não é obrigatório
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': 1,
        })
    )

    # Parâmetros avançados (temperature)
    temperature = forms.FloatField(
        label='Temperatura (Criatividade, 0.1 a 1.0)',
        initial=0.7,
        min_value=0.0,
        max_value=1.0,
        required=False, # Não é obrigatório
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': 0.1, # Permite ajustes de 0.1 em 0.1
        })
    )