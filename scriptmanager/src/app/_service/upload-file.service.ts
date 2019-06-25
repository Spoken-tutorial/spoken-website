import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class UploadFileService {
public testData:FormData = new FormData();

public postFile(tid,file){
  this.testData.append('docs',file);
  const _url = `http://localhost:8000/scripts/api/tutorial/${tid}/scripts/docs/`
  return this.http.post(_url,this.testData);
}
  constructor(public http:HttpClient) { }
}
