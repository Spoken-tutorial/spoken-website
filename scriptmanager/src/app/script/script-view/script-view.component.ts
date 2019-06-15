import { Component, OnInit,Input, Output, EventEmitter } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CreateScriptService } from '../../_service/create-script.service';

@Component({
  selector: 'app-script-view',
  templateUrl: './script-view.component.html',
  styleUrls: ['./script-view.component.sass']
})

export class ScriptViewComponent implements OnInit {
  public slides: any = [];
  private id: number;
  public foss;
  @Input() nav: any;
  public comments: any = [];

  constructor(
    private route: ActivatedRoute,
    public createscriptService: CreateScriptService
  ) { }

  public viewScript() {
    this.createscriptService.getScript(
      this.id
    ).subscribe(
      (res) => {
          this.slides = res;
      },
    );
  }
  


  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
    this.viewScript();
  }

}
