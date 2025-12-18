import React, { useState } from 'react';
import { renderToString } from 'react-dom/server';

function UserBio({ userBio }) {
    return (
        <div dangerouslySetInnerHTML={{ __html: userBio }} />
    );
}

function CommentDisplay({ comment }) {
    const html = `<div class="comment">${comment}</div>`;
    return (
        <div dangerouslySetInnerHTML={{ __html: html }} />
    );
}

function NotificationService({ userMessage }) {
    const scheduleNotification = () => {
        setTimeout(userMessage, 5000);
    };
    
    return <button onClick={scheduleNotification}>Schedule</button>;
}

class ReportComponent extends React.Component {
    render() {
        const { formula } = this.props;
        
        const result = eval(formula);
        
        return <div>Resultado: {result}</div>;
    }
}

function EmailTemplate({ sender, subject, body }) {
    const html = `
        <html>
            <body>
                <h2>De: ${sender}</h2>
                <h1>${subject}</h1>
                <p>${body}</p>
            </body>
        </html>
    `;
    
    return <div dangerouslySetInnerHTML={{ __html: html }} />;
}

function ImageGallery({ userCSS }) {
    return (
        <div>
            <img alt="user" style={userCSS} />
        </div>
    );
}

function FilterComponent({ filterExpression }) {
    const filterFn = new Function('x', `return ${filterExpression}`);
    
    const data = [1, 2, 3, 4, 5];
    const filtered = data.filter(filterFn);
    
    return <div>{filtered.join(', ')}</div>;
}

function LinkGenerator({ destination }) {
    const link = `/redirect?to=${destination}`;
    
    return <a href={link}>Ir</a>;
}

class LivePreview extends React.Component {
    constructor(props) {
        super(props);
        this.previewRef = React.createRef();
    }
    
    componentDidMount() {
        this.previewRef.current.innerHTML = this.props.htmlContent;
    }
    
    render() {
        return <div ref={this.previewRef}></div>;
    }
}

class MessageBox extends React.Component {
    addMessage(userMessage) {
        const div = document.getElementById('messages');
        div.insertAdjacentHTML('beforeend', `<p>${userMessage}</p>`);
    }
    
    render() {
        return <div id="messages"></div>;
    }
}

export default UserBio;
