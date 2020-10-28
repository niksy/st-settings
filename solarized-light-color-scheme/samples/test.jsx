// JSX

const App = () => {
  return (
    <div className="foo">{
      [].map(() => <button type="button" onClick={this.handleClick}></button>)
    }</div>
  );
}
ReactDOM.render(<App />, document.getElementById('app'));
