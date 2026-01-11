const ExcelUploaderViewer = () => {
  const [tableData, setTableData] = React.useState([]);
  const [headers, setHeaders] = React.useState([]);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onload = (evt) => {
      const bstr = evt.target.result;
      const wb = XLSX.read(bstr, { type: 'binary' });
      const wsname = wb.SheetNames[0];
      const ws = wb.Sheets[wsname];
      const data = XLSX.utils.sheet_to_json(ws, { header: 1 });
      
      setHeaders(data[0]);
      setTableData(data.slice(1).map(row => [...row, []])); // 2차 키워드를 위한 빈 배열 추가
    };
    reader.readAsBinaryString(file);
  };

  const handleWordClick = (word, rowIndex) => {
    setTableData(prevData => {
      const newData = [...prevData];
      const keywords = newData[rowIndex][newData[rowIndex].length - 1];
      const index = keywords.indexOf(word);
      if (index === -1) {
        keywords.push(word);
      } else {
        keywords.splice(index, 1);
      }
      return newData;
    });
  };

  const handleAddRow = (rowIndex) => {
    setTableData(prevData => {
      const newData = [...prevData];
      const newRow = [...newData[rowIndex]];
      newRow[newRow.length - 1] = []; // 새 행의 키워드 배열을 초기화
      newData.splice(rowIndex + 1, 0, newRow);
      return newData;
    });
  };

  const handleDeleteRow = (rowIndex) => {
    setTableData(prevData => {
      const newData = [...prevData];
      newData.splice(rowIndex, 1);
      return newData;
    });
  };

  const handleSave = () => {
    const processedData = tableData.map(row => {
      const newRow = [...row];
      newRow[1] = newRow[newRow.length - 1].join(' '); // 2차 키워드를 공백으로 구분된 문자열로 변환
      newRow.pop(); // 마지막 배열 제거
      return newRow;
    });

    const ws = XLSX.utils.json_to_sheet([headers, ...processedData]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
    
    // 파일 저장 (실제 구현에서는 서버로 전송하거나 다운로드 링크를 제공해야 합니다)
    XLSX.writeFile(wb, "processed_data.xlsx");
  };

  const renderCell = (content, rowIndex, colIndex) => {
    if (colIndex === 2) { // '글제목' 열
      const words = content.split(' ');
      return words.map((word, index) => (
        <button
          key={index}
          onClick={() => handleWordClick(word, rowIndex)}
          className={tableData[rowIndex][tableData[rowIndex].length - 1].includes(word) ? 'selected' : ''}
        >
          {word}
        </button>
      ));
    }
    if (colIndex === 1) { // '2차 키워드' 열
      return tableData[rowIndex][tableData[rowIndex].length - 1].join(' ');
    }
    return content;
  };

  return (
    <div className="excel-uploader-viewer">
      <input type="file" accept=".xlsx, .xls" onChange={handleFileUpload} />
      <button onClick={handleSave}>저장하기</button>
      
      {tableData.length > 0 && (
        <table>
          <thead>
            <tr>
              <th></th> {/* 행 추가 버튼을 위한 빈 열 */}
              {headers.map((header, index) => (
                <th key={index}>{header}</th>
              ))}
              <th></th> {/* 행 삭제 버튼을 위한 빈 열 */}
            </tr>
          </thead>
          <tbody>
            {tableData.map((row, rowIndex) => (
              <tr key={rowIndex}>
                <td>
                  <button onClick={() => handleAddRow(rowIndex)}>+</button>
                </td>
                {row.slice(0, -1).map((cell, colIndex) => (
                  <td key={colIndex}>{renderCell(cell, rowIndex, colIndex)}</td>
                ))}
                <td>
                  <button onClick={() => handleDeleteRow(rowIndex)}>삭제</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

ReactDOM.render(<ExcelUploaderViewer />, document.getElementById('root'));